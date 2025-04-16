from typing import List, Optional
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from models.studenProfile import StudentProfile
from models.constContectChunk import ClassContentChunk
from models.claseDinamica import ClaseDinamica
import random

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"
# Tienes estos recursos teóricos:
# {[chunk.model_dump() for chunk in contenido_disponible]}

# Y estos recursos de apoyo visual o multimedia:
# {json.dumps(recursos_apoyo or [], indent=2)}
def plan_clase_dinamica(
    student_profile: StudentProfile,
    clase_descripcion : str,
    unidad_descripcion : str,
    modulo_descripcion : str,
    prueba_nombre : str,
    plan_estudio_nombre:str, 
    nombre_clase : str,
    modulo_nombre : str,
    nombre_unidad: str,
    es_primera_clase: bool,
    contenido_disponible: List[ClassContentChunk] = None,
    recursos_apoyo: Optional[List[dict]] = None
) -> ClaseDinamica:
    """Genera una clase estructurada paso a paso según el flujo pedagógico"""

    if student_profile.intereses:
        intereses_top = ", ".join(random.sample(student_profile.intereses, min(5, len(student_profile.intereses))))
    else:
        intereses_top = "deportes y juegos"
    prompt = f"""
Eres un profesor de {plan_estudio_nombre}, abordando la prueba de {prueba_nombre}. Estás por dictar una clase del módulo {modulo_nombre}, en la unidad {nombre_unidad}, sobre el tema: {nombre_clase}. Esta clase consiste en: {clase_descripcion}.



Es {'la primera clase' if es_primera_clase else 'una clase posterior'} de la unidad.


=== TU TAREA ===
1.⁠ ⁠Eres un profesor de {plan_estudio_nombre} abordando la prueba de {prueba_nombre} en los proximos minutos estaras dictando una clase particular del modulo de {modulo_nombre} {modulo_descripcion},En la unidad {nombre_unidad} {unidad_descripcion}, en la clase la cual consiste en la clase {nombre_clase} la cual consiste en {clase_descripcion}
El alumno tiene intereses en {intereses_top}. Lo que se debería tomar en consideración para los ejemplos y explicación de la materia. 
Generar introducción de la unidad describiendo el tema principal de esta y su utilidad para la vida cotidiana. De ser posible, adecuar a los intereses del alumno. 
2.⁠ ⁠Se debe generar una introducción para abordar en no mas de 1 minuto para la clase explicando el objetivo de esta. 
Luego de esto deberia generar una explicacion y desarrollo del contenido de la clase lo cual no deberia tomar más de 5 minutos. 
Posteriormente se debe entregar al alumno algunos ejemplos que lo ayuden a comprender de mejor manera el contenido de la clase. Dentro de los ejemplos se debe mostrat como se deberia resolver cada uno de estos. Estos ejemplos deberían ser de distintos niveles de dificultad (Al menos uno facil, uno medio y otro dificil). En total, la parte de ejemplos no debería tomar más de 5 minutos.

IMPORTANTE : Utilizar markdowm para mejorar visualmente en desarrollo y ejemplos
RECORDAR: Dar ejemplos relacionado a  {intereses_top}

Que los ejemplos también tengan Markdown




3. **sintesis**: Genera un resumen final de la clase, reforzando los contenidos aprendidos, su utilidad práctica y su vínculo con los intereses del estudiante. Y retroalimentar las correctas

4. **ejercicios_ordenados**: Lista de objetos con:
- Recordar formato
"ejercicios_ordenados": [
  {{
    "enunciado": "¿Cuál es el resultado de 3 x 4?",
    "opciones": ["6", "7", "12", "14", "9"],
    "respuesta_correcta": "12"
  }}
]
   - 5 Ejercicios
  - enunciado
  - opciones (a-e)
  - respuesta_correcta (valor textual)

Ejemplo ejercicios_ordenados:
"ejercicios_ordenados": [
  {{
    "enunciado": "¿Cuál es el resultado de 3 x 4?",
    "opciones": ["6", "7", "12", "14", "9"],
    "respuesta_correcta": "12"
  }}
]

Formato final esperado (en JSON estructurado):
{{
   "introduccion_emocional": "...",
   "repaso_unidad": "...",
   "resumen_clase_anterior": "...",
   "desarrollo": "...",
   "ejemplos": ["...", "..."],
   "ejercicios": ["...", "..."],
   "retroalimentacion": "...",
   "sintesis": "...",
   "recursos_apoyo": [
     {{
        "tipo": "imagen" | "video" | "documento",
        "descripcion": "...",
        "etapa_uso": "introduccion" | "desarrollo" | "ejemplos" | "ejercicios" | "sintesis",
        "url": "https://..."
     }}
   ],
   "ejercicios_ordenados": [
     {{
        "enunciado": "...",
        "opciones": ["a", "b", "c", "d", "e"],
        "respuesta_correcta": "..."
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
