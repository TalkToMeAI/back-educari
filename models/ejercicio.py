from pydantic import BaseModel
from typing import List





class Ejercicio(BaseModel):
    enunciado: str
    opciones: List[str]
    respuesta_correcta: str

