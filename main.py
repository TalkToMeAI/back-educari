from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from services.openai_client import OpenAIChatClient
from services.mathAgent import plan_clase_dinamica
from services.chatSupervisor import SupervisarClaseRequest, ChatbotDecision, manejar_chat_pedagogico_con_clase
from services.teacherMath import clase_personalizada
from services.classSupabase import generar_clase_dinamica_sin_chunks
from dotenv import load_dotenv
from models.studenProfile import StudentProfile
from models.constContectChunk import ClassContentChunk
from services.synthesis import generar_sintesis 

from fastapi.responses import JSONResponse
import re
import json

load_dotenv()

chat_client = OpenAIChatClient()
app = FastAPI()

# ✅ Lista de orígenes permitidos (agrega todos los necesarios)
origins = [
    "https://app.educari.cl",
    "https://educari-front.vercel.app",
    "https://educari-front-git-develop-jorge-oehrens-projects.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# ✅ Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],             # permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],             # permitir todos los headers
)

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = "gpt-4o"
    system_prompt: str | None = "You're a helpful assistant."


class ClaseInput(BaseModel):
    clase: str
    modulo: str
    unidad: str


routes = APIRouter()

@app.get("/")
def read_root():
    return {"Educari": "World"}

@app.post("/chat")
def chat(request: ChatRequest):
    response = chat_client.chat(
        messages=request.messages,
        model=request.model,
        system_prompt=request.system_prompt
    )
    return {"response": response}

@app.post("/clase/dinamica")
def crear_clase_dinamica(
    profile: StudentProfile,
    materia: str,
    unidad: str,
    modulo: str,
    programa: str,
    clase: str,
    descripcion_clase: str,
    es_primera_clase: bool,
    contenido: List[ClassContentChunk]
):
    return plan_clase_dinamica(
        student_profile=profile,
        materia=materia,
        unidad=unidad,
        modulo=modulo,
        programa=programa,
        clase=clase,
        descripcion_clase=descripcion_clase,
        es_primera_clase=es_primera_clase,
        contenido_disponible=contenido
    )

@app.post("/clase/chatbot/supervisar", response_model=ChatbotDecision)
def supervisar_chat_de_clase(request: SupervisarClaseRequest):
    return manejar_chat_pedagogico_con_clase(
        perfil=request.perfil,
        historial=request.historial,
        clase=request.clase_generada
    )

@app.post("/clase/recursos")
def crear_clase_recursos(id_estudiante: str, id_clase: str):
    return clase_personalizada(
        id_estudiante=id_estudiante,
        id_clase=id_clase
    )

@app.post("/clase/ia")
def crear_clase_ia(id_estudiante: str, id_clase: str):
    return generar_clase_dinamica_sin_chunks(
        id_estudiante=id_estudiante,
        id_clase=id_clase
    )

@app.post("/clase/ia2")
def crear_clase_ia2(id_estudiante: str, id_clase: str):
    return generar_clase_dinamica_sin_chunks(
        id_estudiante=id_estudiante,
        id_clase=id_clase
    )



@app.post("/clase/sintesis")
async def crear_clase_sintesis(data: ClaseInput):
    try:
        result_str = generar_sintesis(data.clase, data.modulo, data.unidad)

        # Extraer solo el JSON válido (en caso de que haya texto adicional)
        match = re.search(r"\{[\s\S]*\}", result_str)
        if not match:
            raise ValueError("No se encontró JSON válido en la respuesta.")

        parsed = json.loads(match.group(0))
        return JSONResponse(content=parsed)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
