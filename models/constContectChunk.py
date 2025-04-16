from pydantic import BaseModel
from typing import Literal



class ClassContentChunk(BaseModel):
    id: str
    texto: str
    tema: str
    dificultad: Literal["básico", "intermedio", "avanzado"]
    tipo_contenido: Literal["teoría", "ejemplo", "ejercicio"]

