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
    nombre_clase_anterior: str ,
    descripcion_clase_anterior :  str

) -> ClaseDinamica:


    if student_profile.intereses:
        intereses_top = ", ".join(random.sample(student_profile.intereses, min(5, len(student_profile.intereses))))
    else:
        intereses_top = "deportes y juegos"



    prompt = f"""
Eres un profesor de {plan_estudio_nombre}, abordando la asignatura de {prueba_nombre}. En los próximos minutos estarás dictando una clase particular del módulo 
módulo {modulo_nombre}, correspondiente a la unidad {nombre_unidad}, la cual consiste en {clase_descripcion}. En específicio {nombre_clase}. Cuyo objetivo es enseñar al alumno sobre {clase_descripcion}.

Durante toda la clase debes considerar los intereses del estudiante: {intereses_top}. Por lo tanto: 
  - Utiliza ejemplos, explicaciones y situaciones relacionadas a esos intereses para favorecer la comprensión del contenido. 
  - Contextualiza los ejercicios y problemas, siempre que sea posible, conectándolos a {intereses_top}. 
El contenido debe estar en formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown.
  
 Ahora desarrollarás la clase de la siguiente manera:

1. Introducción: 
  Generar introducción de la unidad {nombre_unidad}, describiendo el tema principal de esta y su utilidad para la vida cotidiana. De ser posible, adecuar a los intereses del alumno.

  
2. Repaso de la unidad:

{f"""Crear un resumen de la clase **{nombre_clase_anterior}**, cuyo contenido fue: *{descripcion_clase_anterior}*. El resumen debe durar no más de 3 minutos y enfocarse en los aspectos procedimentales y conceptuales. Se debe asumir que el alumno ya cursó esta clase, por lo que se trata de un recordatorio.""" if es_primera_clase else "No generar repaso, ya que esta clase inicia una nueva unidad."}
  -  IMPORTANTE : El contenido debe estar en formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown.

3. Desarrollo:
  - Desarrolla el contenido de la clase de forma detallada y paso a paso (no solo conceptual). 
  - Explica todos los procedimientos o algoritmos involucrados, mostrando el razonamiento detrás de cada paso. 
  -  IMPORTANTE : El contenido debe estar en formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown.

4. Ejemplos:
  - Incluye tres ejemplos resueltos: 
      Uno de nivel fácil, 
      Uno de nivel medio, 
      Uno de nivel difícil tipo PAES M1 (problema contextualizado). 
  - Propón ejercicios que requieran ser desarrollados con lápiz y papel (evita ejercicios de simple cálculo mental). 
  . 

5. Ejercicios : 
  - formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown
  - Propón **ejercicios que requieran ser desarrollados con lápiz y papel** (evita ejercicios de simple cálculo mental).
  - Genera 3 a 4 ejercicios que el estudiante debe resolver con lápiz y papel. Varía el nivel de dificultad: 1 fácil, 1 medio, 2 difíciles (tipo PAES M1).  Cada ejercicio debe considerar 5 alternativas cada uno, identificadas con una letra desde la “a” hasta la “e” en el comienzo de cada opción, en donde solo debería haber una correcta (de manera aleatoria, la respuesta correcta debería ser una de esas 5). La respuesta correcta no se debe mostrar al alumno, para que este pueda responder. 
  - "ejercicios_ordenados": [
  {{
    "enunciado": "¿Cuál es el resultado de 3 x 4?",
    "opciones": ["6", "7", "12", "14", "9"],
    "respuesta_correcta": "12"
  }}
]
  - enunciado
  - opciones (a-e)
  - respuesta_correcta
  - Variar en que cada ejercicio la respuesta correcta sea una de las 5 opciones, de manera aleatoria.
  - IMPORTANTE : El contenido debe estar en formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown.
desarrollo y ejemplos
  - RECORDAR: Dar ejemplos relacionado a  {intereses_top}
  - formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown


Que los ejemplos también tengan Markdown
6. Sintesis:
  - Genera una síntesis de la clase {nombre_clase} del módulo {modulo_nombre}, correspondiente a la unidad 
  -  IMPORTANTE : El contenido debe estar en formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown.

  - En esta síntesis debes incluir obligatoriamente: 
    
    Contenidos Abordados:   
      - Haz un repaso claro y ordenado de los conceptos principales trabajados en esta clase.  
      - Menciona explícitamente las ideas clave, los procedimientos vistos y los tipos de ejercicios que se practicaron. 
    
    Fortalezas del estudiante: 
      - Indica en qué aspectos el estudiante mostró mayor dominio, precisión o agilidad. 
      - Ejemplifica con algún tipo de ejercicio o contenido donde haya demostrado comprensión o éxito. 
    
    Debilidades o Dificultades: 
      - Señala claramente qué aspectos costaron más al estudiante. 
      - Explica si hubo errores recurrentes, confusiones en pasos específicos, o dificultades en tipos de ejercicios. 
      
    Tips paso a paso para mejorar: 
      - Entrega 3 a 5 recomendaciones concretas y accionables para que el estudiante pueda mejorar. 
      - Cada tip debe ser breve, práctico y relacionado directamente al contenido de esta clase. 
      - Ordena los tips en formato de pasos (Paso 1, Paso 2, etc.) para que el estudiante sepa exactamente cómo avanzar. 
  - Vincula algún consejo extra con los intereses del alumno ({intereses_top}), para motivarlo aún más a mejorar. 

  
Formato final esperado (en JSON estructurado):
  - No agregues el titulo de cada etapa 
  - IMPORTANTE : El contenido debe estar en formato Markdown y usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown.
  -  usar fórmulas matemáticas escritas en LaTeX entre símbolos $ para que puedan renderizarse con KaTeX en ReactMarkdown

  

desarrollo y ejemplos
{{
   "introduccion_emocional": "...",
   "repaso_unidad": "...",
   "resumen_clase_anterior": "...",
   "desarrollo": "...",
   "ejemplos": ["...", "..."],
   "ejercicios": ["...", "..."],
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
