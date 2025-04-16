from typing import List, Optional
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import json
from models.studenProfile import StudentProfile
from models.constContectChunk import ClassContentChunk
from models.claseDinamica import ClaseDinamica
from models.claseEstadoActual import ClaseEstadoActual


# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

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
