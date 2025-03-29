from services.teacherMath import clase_personalizada
from services.mathAgent import plan_clase_dinamica, StudentProfile, ClassContentChunk

def generar_clase_dinamica_sin_chunks(id_estudiante: str, id_clase: str):
    datos = clase_personalizada(id_estudiante=id_estudiante, id_clase=id_clase)
    print("🧩 Datos recibidos desde clase_personalizada:", datos)

    # Asegurar que "clase" existe y tiene las claves necesarias
    clase = datos.get("clase", {})
    materia = clase.get("materia", "materia no especificada")
    unidad = clase.get("unidad", "unidad no especificada")
    modulo = clase.get("modulo", "modulo no especificado")
    nombre_clase = clase.get("nombre", "nombre no especificado")
    descripcion = clase.get("descripcion", "sin descripción")
    es_primera = clase.get("es_primera_clase", True)

    # 🧠 Construir perfil del estudiante
    profile = StudentProfile(
        personalidad="reflexivo y constante",
        intereses=[i.get("interes", "sin especificar") for i in datos.get("intereses_estudiante", [])],
        estilo_aprendizaje="visual",  # Puedes adaptar esto con base en otros datos del alumno
        nivel_conocimiento={
            "matemáticas": "intermedio"
        },
        estado_emocional="motivado"
    )

    print("🎯 Perfil del estudiante generado:", profile)

    # No hay chunks disponibles
    contenido = []

    # ✅ Llamar al planificador
    clase_generada = plan_clase_dinamica(
        student_profile=profile,
        materia=materia,
        unidad=unidad,
        modulo=modulo,
        programa="Matemática 7º Básico",
        clase=nombre_clase,
        descripcion_clase=descripcion,
        es_primera_clase=es_primera,
        contenido_disponible=contenido
    )

    print("✅ Clase generada:", clase_generada)

    return clase_generada
