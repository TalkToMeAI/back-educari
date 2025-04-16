from typing import List, Literal, Optional
from pydantic import BaseModel





class ClaseEstadoActual(BaseModel):
    etapa_actual: Literal["introduccion", "repaso", "desarrollo", "ejemplos", "ejercicios", "retroalimentacion", "final"]
    respuestas_alumno: Optional[List[str]] = None
    respuestas_correctas: Optional[List[int]] = None
    accion_usuario_actual: Optional[str] = None
    estado_emocional: Literal["mal", "inseguro", "motivado"]
