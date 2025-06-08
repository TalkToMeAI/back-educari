from services.teacherMath import clase_personalizada
from services.mathAgent import plan_clase_dinamica, StudentProfile, ClassContentChunk

def generar_clase_dinamica_sin_chunks(id_estudiante: str, id_clase: str):


    datos = clase_personalizada(id_estudiante=id_estudiante, id_clase=id_clase)


    clase = datos.get("clase", {})
    unidad = datos.get("unidad", {})
    modulo = datos.get("modulo", {})
    prueba = datos.get("prueba", {})

    clase_anterior = datos.get("clase_anterior", {})


    plan_estudio = datos.get("plan_estudio", {})
    contenido_data = datos.get("contenido_completo", {})
    recursos_apoyo = [
        {
            "tipo": "imagen",
            "descripcion": recurso.get("descripcion", ""),
            "etapa_uso": recurso.get("etapa", "desarrollo"),
            "url": recurso.get("data", "")
        }
        for recurso in contenido_data
        if recurso.get("data")
    ]


    nombre_clase = clase.get("titulo", "nombre no especificado")
    clase_descripcion = clase.get("descripcion", "sin descripción")  # <-- Agrega esta línea
    unidad_descripcion = unidad.get("descripcion", "sin descripción")
    nombre_unidad =  unidad.get("titulo", "sin descripción")
    id_unidad =  unidad.get("id", "sin id")

    modulo_descripcion = modulo.get("descripcion", "sin descripción")
    modulo_nombre = modulo.get("titulo", "sin descripción")
    prueba_nombre = prueba.get("nombre", "sin descripción")
    plan_estudio_nombre = plan_estudio.get("nombre", "sin descripción")

    if not clase_anterior or not clase_anterior.get("contenido_id"):
        es_primera = True
        nombre_clase_anterior = ""
        descripcion_clase_anterior = ""
    else:
        nombre_clase_anterior = clase_anterior.get("titulo", "sin descripción")
        descripcion_clase_anterior = clase_anterior.get("descripcion", "sin descripción")
        contenido_clase_anterior = clase_anterior.get("contenido_id", "sin contenido")
        es_primera = str(contenido_clase_anterior) == str(id_unidad)


    profile = StudentProfile(
        personalidad="reflexivo y constante",
        intereses=[i.get("interes_nombre", "sin especificar") for i in datos.get("intereses_estudiante", [])],
        estilo_aprendizaje="visual",  # Puedes adaptar esto con base en otros datos del alumno
        nivel_conocimiento={
            "matemáticas": "intermedio"
        },
        estado_emocional="motivado"
    )


    # No hay chunks disponibles
    contenido = []

    # ✅ Llamar al planificador
    clase_generada = plan_clase_dinamica(
        student_profile=profile,
        clase_descripcion= clase_descripcion,
        unidad_descripcion = unidad_descripcion,
        modulo_descripcion = modulo_descripcion,
        prueba_nombre = prueba_nombre,
        plan_estudio_nombre = plan_estudio_nombre,
        nombre_clase = nombre_clase,
        modulo_nombre = modulo_nombre,
        nombre_unidad = nombre_unidad,
        es_primera_clase = es_primera,
        nombre_clase_anterior = nombre_clase_anterior,
        descripcion_clase_anterior = descripcion_clase_anterior,
    )
    clase_generada.recursos_apoyo = recursos_apoyo


    return clase_generada
