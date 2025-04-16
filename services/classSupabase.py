from services.teacherMath import clase_personalizada
from services.mathAgent import plan_clase_dinamica, StudentProfile, ClassContentChunk

def generar_clase_dinamica_sin_chunks(id_estudiante: str, id_clase: str):


    datos = clase_personalizada(id_estudiante=id_estudiante, id_clase=id_clase)
    print("🧩 Datos recibidos desde clase_personalizada:", datos)


    clase = datos.get("clase", {})
    unidad = datos.get("unidad", {})
    modulo = datos.get("modulo", {})
    prueba = datos.get("prueba", {})
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
    unidad_descripcion = unidad.get("descripcion", "sin descripción")
    nombre_unidad =  unidad.get("titulo", "sin descripción")
    modulo_descripcion = modulo.get("descripcion", "sin descripción")
    modulo_nombre = modulo.get("titulo", "sin descripción")
    prueba_nombre = prueba.get("nombre", "sin descripción")
    plan_estudio_nombre = plan_estudio.get("nombre", "sin descripción")



    clase_descripcion = clase.get("descripcion", "sin descripción")
    es_primera = clase.get("es_primera_clase", True)

    print(f"""
        📘 Información de la clase:\
          
        - clase_descripcion: {clase_descripcion}
        - Unidad_descripcion: {unidad_descripcion}
        - Módulo: {modulo_descripcion}
        - Prueba: {prueba_nombre}
        - Plan Estudio: {plan_estudio_nombre}
        - Nombre de la clase: {nombre_clase}
        - ¿Es la primera clase?: {"Sí" if es_primera else "No"}

        """)




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
        es_primera_clase = "false"


   
    )
    clase_generada.recursos_apoyo = recursos_apoyo


    return clase_generada
