from typing import List, Optional
from pydantic import BaseModel
from models.ejercicio import Ejercicio





class ClaseDinamica(BaseModel):
    introduccion_emocional: str
    repaso_unidad: Optional[str]
    resumen_clase_anterior: Optional[str]
    desarrollo: str
    ejemplos: List[str]
    ejercicios: List[str]
    ejercicios_ordenados: Optional[List[Ejercicio]] = None  # ← Nuevo campo

    retroalimentacion: str
    sintesis: str
    recursos_apoyo: Optional[List[dict]] = None  # 🔥 Nuevo campo
