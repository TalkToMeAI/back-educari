from pydantic import BaseModel
from typing import List, Literal



class StudentProfile(BaseModel):
    personalidad: str
    intereses: List[str]
    estilo_aprendizaje: Literal["visual", "auditivo", "kinestésico", "lectura/escritura"]
    nivel_conocimiento: dict
    estado_emocional: Literal["mal", "inseguro", "motivado"]
