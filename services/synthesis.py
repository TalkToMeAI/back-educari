from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

def generar_sintesis(clase: str, modulo: str, unidad: str) -> str:
    prompt = f"""
Eres un profesor experto en educación pedagógica.

Genera una **síntesis** de la clase {clase} del módulo {modulo}, correspondiente a la unidad {unidad}.

La salida debe estar en formato **JSON válido**, con esta estructura:

{{
  "sintesis": "<contenido en Markdown, usando fórmulas en LaTeX entre $...$>"
}}

⚠️ Instrucciones:
- NO escribas nada fuera del bloque JSON.
- NO uses comillas dobles sin escapar.
- El contenido debe estar en Markdown y usar $...$ para fórmulas matemáticas en LaTeX.
- Usa párrafos separados o puntos aparte para que sea más claro para estudiantes.
"""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Eres un generador de contenido educativo para estudiantes de secundaria."},
            {"role": "user", "content": prompt}
        ]
    )

    content = completion.choices[0].message.content
    logger.info("Síntesis generada correctamente.")
    return content
