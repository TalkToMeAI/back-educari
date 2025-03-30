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
    nivel_conocimiento: dict
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
    recursos_apoyo: Optional[List[dict]] = None  # 🔥 Nuevo campo

class ClaseEstadoActual(BaseModel):
    etapa_actual: Literal["introduccion", "repaso", "desarrollo", "ejemplos", "ejercicios", "retroalimentacion", "final"]
    respuestas_alumno: Optional[List[str]] = None
    respuestas_correctas: Optional[List[int]] = None
    accion_usuario_actual: Optional[str] = None
    estado_emocional: Literal["mal", "inseguro", "motivado"]

# --------------------------------------------------------------
# Step 2: Transformador de contenido en recursos visuales
# --------------------------------------------------------------

def transformar_contenido_a_recursos(contenido_completo: List[dict]) -> List[dict]:
    recursos = []
    for item in contenido_completo:
        etapa_original = item.get("etapa", "").lower()
        if "introduccion" in etapa_original:
            etapa = "introduccion"
        elif "repaso" in etapa_original:
            etapa = "repaso"
        elif "desarrollo" in etapa_original:
            etapa = "desarrollo"
        elif "ejemplos" in etapa_original:
            etapa = "ejemplos"
        elif "ejercicios" in etapa_original:
            etapa = "ejercicios"
        elif "retroalimentacion" in etapa_original:
            etapa = "retroalimentacion"
        elif "resumen" in etapa_original or "sintesis" in etapa_original:
            etapa = "sintesis"
        else:
            etapa = "desarrollo"

        recurso = {
            "tipo": "imagen" if item.get("tipo") == "banco_fotos" else item.get("tipo"),
            "descripcion": item.get("descripcion", "Recurso sin descripción"),
            "etapa_uso": etapa,
            "url": item.get("data")
        }
        recursos.append(recurso)
    return recursos

# --------------------------------------------------------------
# Step 3: Agente para generar clase dinámica
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
    contenido_disponible: List[ClassContentChunk],
    recursos_apoyo: Optional[List[dict]] = None
) -> ClaseDinamica:
    """Genera una clase estructurada paso a paso según el flujo pedagógico"""

    logger.info(f"Generando clase dinámica para {materia} - {clase} - estado emocional: {student_profile.estado_emocional}")

    prompt = f"""
Eres un profesor experto en {programa}, dictando una clase de la asignatura {materia}, módulo {modulo}, unidad {unidad}, tema: "{clase}".
Esta clase trata sobre: "{descripcion_clase}".

Perfil del estudiante:
{student_profile.model_dump_json(indent=2)}

Es {'la primera clase' if es_primera_clase else 'una clase posterior'} de la unidad.

Tienes estos recursos teóricos:
{[chunk.model_dump() for chunk in contenido_disponible]}

Y estos recursos de apoyo visual o multimedia:
{json.dumps(recursos_apoyo or [], indent=2)}

=== TU TAREA ===

Genera una clase interactiva en formato JSON con los siguientes campos. En cada etapa, INTEGRA recursos visuales o multimedia si están disponibles. Por ejemplo:

- Si en desarrollo hay una imagen que explica un concepto, inclúyela con algo como: "Observa la imagen [nombre o descripción] aquí: [URL]".
- En ejemplos o ejercicios, si hay un video o imagen de apoyo, úsala como complemento visual.
- No repitas los recursos dos veces, úsalos solo en la etapa que corresponde.

Formato final esperado:

{{
  "introduccion_emocional": "Saludo inicial empático...",
  "repaso_unidad": "Si es la primera clase, explicar unidad. Si no, omitir o breve mención.",
  "resumen_clase_anterior": "Solo si no es la primera clase",
  "desarrollo": "Explicación del contenido usando recursos visuales si aplica. Integrar imágenes con URLs y descripciones cuando sea posible.",
  "ejemplos": [
    "Ejemplo 1 explicado paso a paso. Ver imagen: https://...",
    "Ejemplo 2..."
  ],
  "ejercicios": [
    "Ejercicio 1 (opciones a-e)",
    "Ejercicio 2..."
  ],
  "retroalimentacion": "Mensajes según respuestas correctas/incorrectas",
  "sintesis": "Resumen final que refuerce los aprendizajes. Puedes usar recursos si hay.",
  "recursos_apoyo": [
    {{
      "tipo": "imagen" | "video" | "documento",
      "descripcion": "¿Qué explica o ilustra este recurso?",
      "etapa_uso": "introduccion" | "desarrollo" | "ejemplos" | "ejercicios" | "sintesis",
      "url": "https://..."
    }}
  ]
}}
"""

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Eres un generador de clases interactivas que usa recursos visuales y adapta el contenido al estado emocional y estilo del estudiante."
            },
            {"role": "user", "content": prompt}
        ],
        response_format=ClaseDinamica,
    )

    result = completion.choices[0].message.parsed
    logger.info("Clase dinámica generada correctamente con integración de imágenes y recursos")
    return result

# --------------------------------------------------------------
# Step 4: Agente supervisor de progreso
# --------------------------------------------------------------

def supervisar_progreso_clase(
    estado: ClaseEstadoActual,
    perfil: StudentProfile
) -> dict:
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
