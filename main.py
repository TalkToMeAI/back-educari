from fastapi import FastAPI,APIRouter
# from api.controllers import products, ingredients,video_tutorial, preparation, recipe

from pydantic import BaseModel
from typing import List, Literal

from services.openai_client import OpenAIChatClient
from services.mathAgent import plan_clase_dinamica, StudentProfile, ClassContentChunk
from services.chatSupervisor import SupervisarClaseRequest, ChatbotDecision, manejar_chat_pedagogico_con_clase

from dotenv import load_dotenv
load_dotenv()

chat_client = OpenAIChatClient()
app = FastAPI()

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = "gpt-4o"
    system_prompt: str | None = "You're a helpful assistant."


routes = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "World"}


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
    """
    Endpoint para evaluar la interacción del alumno durante una clase dinámica
    y decidir si debe avanzar, repetir, recibir ayuda o cerrar la clase.
    """
    return manejar_chat_pedagogico_con_clase(
        perfil=request.perfil,
        historial=request.historial,
        clase=request.clase_generada
    )

# {
#   "messages": [
#     {
#       "role": "user",
#       "content": "Hello, how are you?"
#     }
#   ],
#   "model": "gpt-4o",
#   "system_prompt": "You're a helpful assistant."
# }