from typing import List, Literal, Optional
from pydantic import BaseModel
from services.mathAgent import StudentProfile, ClaseDinamica  # donde definiste esos modelos
import logging

logger = logging.getLogger(__name__)


class ClaseHistorial(BaseModel):
    etapa_actual: Literal[
        "introduccion",
        "repaso",
        "desarrollo",
        "ejemplos",
        "ejercicios",
        "retroalimentacion",
        "final"
    ]
    acciones_previas: List[str] = []
    respuestas_alumno: Optional[List[str]] = None  # ["1-a", "2-c"]
    respuestas_correctas: Optional[List[int]] = None  # [1, 3]
    estado_emocional: Literal["mal", "inseguro", "motivado"]
    accion_usuario_actual: str  # input actual del usuario




class SupervisarClaseRequest(BaseModel):
    perfil: StudentProfile
    historial: ClaseHistorial
    clase_generada: ClaseDinamica


class ClaseHistorial(BaseModel):
    etapa_actual: Literal["introduccion", "repaso", "desarrollo", "ejemplos", "ejercicios", "retroalimentacion", "final"]
    acciones_previas: List[str] = []  # ej: ["mostrar_ejemplos", "repetir_etapa"]
    respuestas_alumno: Optional[List[str]] = None  # ["1-a", "2-c"]
    respuestas_correctas: Optional[List[int]] = None  # [1, 3]
    estado_emocional: Literal["mal", "inseguro", "motivado"]
    accion_usuario_actual: str  # input actual del usuario

class ChatbotDecision(BaseModel):
    accion: str  # "repetir_etapa", "mostrar_ejemplos_adicionales", "pasar_a_siguiente_etapa", etc.
    justificacion: str
    nueva_etapa: Optional[str] = None  # si cambia la etapa
    mensaje_bot: str  # respuesta del bot al estudiante

def supervisar_progreso_clase(estado: ClaseHistorial, perfil: StudentProfile) -> dict:
    """
    Supervisa el progreso del alumno y determina la siguiente acción pedagógica.
    """
    # Evaluar estado emocional y desempeño
    if estado.estado_emocional == "mal":
        return {
            "accion": "entregar_ayuda",
            "justificacion": "El estudiante necesita apoyo adicional"
        }
    
    # Si hay respuestas incorrectas en ejercicios
    if (estado.respuestas_alumno and estado.respuestas_correctas and
        len(estado.respuestas_alumno) != sum(estado.respuestas_correctas)):
        return {
            "accion": "mostrar_ejemplos_adicionales",
            "justificacion": "El estudiante necesita más práctica"
        }
    
    # Si el estudiante está inseguro
    if estado.estado_emocional == "inseguro":
        return {
            "accion": "repetir_etapa",
            "justificacion": "Reforzar la comprensión del tema"
        }
    
    # Si todo va bien, avanzar
    if estado.estado_emocional == "motivado":
        return {
            "accion": "pasar_a_siguiente_etapa",
            "justificacion": "El estudiante está listo para avanzar"
        }
    
    # Por defecto, continuar con la etapa actual
    return {
        "accion": "continuar",
        "justificacion": "Mantener el ritmo actual de la clase"
    }

def manejar_chat_pedagogico_con_clase(
    perfil: StudentProfile,
    historial: ClaseHistorial,
    clase: ClaseDinamica
) -> ChatbotDecision:
    """
    Integra el contenido generado de la clase con el historial del alumno.
    """
    decision = supervisar_progreso_clase(estado=historial, perfil=perfil)
    accion = decision.get("accion", "error")

    # Personaliza el mensaje en base a etapa y contenido
    if accion == "mostrar_ejemplos_adicionales":
        mensaje = "Aquí van más ejemplos: \n" + "\n".join(clase.ejemplos[-2:])
    elif accion == "repetir_etapa":
        mensaje = "Revisemos esta parte de nuevo: \n" + clase.desarrollo
    elif accion == "pasar_a_siguiente_etapa":
        mensaje = "¡Perfecto! Sigamos con la siguiente parte de la clase."
    elif accion == "entregar_ayuda":
        mensaje = "Aquí va una explicación complementaria: \n" + clase.retroalimentacion
    elif accion == "terminar_clase":
        mensaje = clase.sintesis + "\n¡Clase finalizada!"
    else:
        mensaje = "Hubo un problema al evaluar tu progreso."

    return ChatbotDecision(
        accion=accion,
        justificacion=decision.get("justificacion", ""),
        nueva_etapa=determinar_etapa_siguiente(historial.etapa_actual, accion),
        mensaje_bot=mensaje
    )


def determinar_etapa_siguiente(etapa_actual: str, accion: str) -> Optional[str]:
    orden_etapas = [
        "introduccion",
        "repaso",
        "desarrollo",
        "ejemplos",
        "ejercicios",
        "retroalimentacion",
        "final"
    ]
    if accion == "pasar_a_siguiente_etapa":
        idx = orden_etapas.index(etapa_actual)
        return orden_etapas[min(idx + 1, len(orden_etapas) - 1)]
    return etapa_actual
