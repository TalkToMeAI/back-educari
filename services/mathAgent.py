from typing import List, Literal, Optional
from pydantic import BaseModel
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import json

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

# --------------------------------------------------------------
# Step 1: Data Models
# --------------------------------------------------------------

class StudentProfile(BaseModel):
    personalidad: str
    intereses: List[str]
    estilo_aprendizaje: Literal["visual", "auditivo", "kinestésico", "lectura/escritura"]
    nivel_conocimiento: dict  # e.g. {"matemáticas": "intermedio"}
    estado_emocional: Literal["mal", "inseguro", "motivado"]

class ClassContentChunk(BaseModel):
    id: str
    texto: str
    tema: str
    dificultad: Literal["básico", "intermedio", "avanzado"]
    tipo_contenido: Literal["teoría", "ejemplo", "ejercicio"]

class ClaseDinamica(BaseModel):
    introduccion_emocional: str
    repaso_unidad: Optional[str]
    resumen_clase_anterior: Optional[str]
    desarrollo: str
    ejemplos: List[str]
    ejercicios: List[str]
    retroalimentacion: str
    sintesis: str

class ClaseEstadoActual(BaseModel):
    etapa_actual: Literal["introduccion", "repaso", "desarrollo", "ejemplos", "ejercicios", "retroalimentacion", "final"]
    respuestas_alumno: Optional[List[str]] = None  # Ej: ["1-a", "2-c"]
    respuestas_correctas: Optional[List[int]] = None  # Ej: [1, 3]
    accion_usuario_actual: Optional[str] = None  # Ej: "Necesito más ejemplos"
    estado_emocional: Literal["mal", "inseguro", "motivado"]

# --------------------------------------------------------------
# Step 2: Agente para generar clase dinámica
# --------------------------------------------------------------

def plan_clase_dinamica(
    student_profile: StudentProfile,
    materia: str,
    unidad: str,
    modulo: str,
    programa: str,
    clase: str,
    descripcion_clase: str,
    es_primera_clase: bool,
    contenido_disponible: List[ClassContentChunk]
) -> ClaseDinamica:
    """Genera una clase estructurada paso a paso según el flujo pedagógico"""

    logger.info(f"Generando clase dinámica para {materia} - {clase} - estado emocional: {student_profile.estado_emocional}")

    prompt = f"""
Eres un profesor de {programa}, abordando la asignatura de {materia}. Estás por dictar una clase del módulo {modulo}, en la unidad {unidad}, sobre el tema: {clase}. Esta clase consiste en: {descripcion_clase}.

El estudiante tiene el siguiente perfil:
{student_profile.model_dump_json(indent=2)}

Es {'la primera clase' if es_primera_clase else 'una clase posterior'} de la unidad.

Tienes disponibles los siguientes contenidos:
{[chunk.model_dump() for chunk in contenido_disponible]}

=== Tu tarea es generar una clase dinámica estructurada con los siguientes campos JSON: ===

{{
  "introduccion_emocional": "Saludo inicial y respuesta empática según el estado emocional",
  "repaso_unidad": "Si es primera clase, introducir unidad; si no, omitir",
  "resumen_clase_anterior": "Si no es primera clase, incluir resumen",
  "desarrollo": "Explicación adaptada al estado emocional y nivel del alumno",
  "ejemplos": ["Ejemplo 1 resuelto", "Ejemplo 2 resuelto", "..."],
  "ejercicios": ["Ejercicio 1 con opciones a-e", "Ejercicio 2...", "..."],
  "retroalimentacion": "Texto para retroalimentar según respuestas correctas/incorrectas",
  "sintesis": "Resumen final de la clase, reforzando utilidad del contenido y vínculo con sus intereses"
}}
"""

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Eres un generador de clases interactivas y personalizadas según emociones, intereses y contenidos."
            },
            {"role": "user", "content": prompt}
        ],
        response_format=ClaseDinamica,
    )

    result = completion.choices[0].message.parsed
    logger.info("Clase dinámica generada correctamente")
    return result

# --------------------------------------------------------------
# Step 3: Agente supervisor de progreso
# --------------------------------------------------------------

def supervisar_progreso_clase(
    estado: ClaseEstadoActual,
    perfil: StudentProfile
) -> dict:
    """
    Evalúa si el alumno debe repetir la etapa, avanzar, recibir ayuda o finalizar la clase.
    Devuelve un dict con "accion" y "justificacion".
    """

    logger.info(f"Evaluando progreso del estudiante en etapa: {estado.etapa_actual}")

    prompt = f"""
Estás supervisando una clase interactiva de matemáticas.

Etapa actual: {estado.etapa_actual}
Estado emocional del estudiante: {estado.estado_emocional}
Acción reciente del estudiante: {estado.accion_usuario_actual}
Respuestas del alumno: {estado.respuestas_alumno}
Respuestas correctas: {estado.respuestas_correctas}

Perfil del alumno:
{perfil.model_dump_json(indent=2)}

Basado en este contexto, responde en formato JSON con la acción a tomar y su justificación. Opciones:

- "repetir_etapa"
- "entregar_ayuda"
- "mostrar_ejemplos_adicionales"
- "pasar_a_siguiente_etapa"
- "terminar_clase"

Formato:
{{
  "accion": "string",
  "justificacion": "string"
}}
"""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Eres un agente supervisor pedagógico con criterio para guiar clases."},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        logger.warning("No se pudo interpretar la respuesta del LLM. Devuelve texto sin parsear.")
        return {"accion": "error", "justificacion": str(e)}
