from pydantic import BaseModel

class Student(BaseModel):
    name: str         # Nombre del estudiante
    age: int          # Edad del estudiante
    year: int         # Año de estudio (ej. 1, 2, 3, etc.)
    email: str        # Correo electrónico del estudiante