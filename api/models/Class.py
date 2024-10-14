from pydantic import BaseModel
from api.models.Student import Student  # Importar el modelo Student

class Class(BaseModel):
    asignature: str  # Asignatura de la clase (ej. Historia)
    module: str      # Módulo dentro de la asignatura
    student: Student     # Nombre del estudiante
    question: str    # Pregunta del estudiante
    topic: str       # Tema del módulo
    question_number: int  # Número de pregunta (ayuda a la lógica del flujo de la clase)