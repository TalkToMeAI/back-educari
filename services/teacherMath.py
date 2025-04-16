import os
from supabase import create_client, Client
from dotenv import load_dotenv
from services.resourcesClass import explicar_imagen_usando_vision  # ✅ importa tu función vision

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def clase_personalizada(id_estudiante: str, id_clase: str):
    # 1. Datos de la clase
    clase_data = supabase.table("clase").select("*").eq("id", id_clase).single().execute().data

    unidad_data_id = clase_data.get("contenido_id")
    unidad_data = supabase.table("unidad").select("*").eq("id", unidad_data_id).single().execute().data

    modulo_data_id = unidad_data.get("modulo_id")
    modulo_data = supabase.table("modulo").select("*").eq("id", modulo_data_id).single().execute().data
    asignatura_data_id = modulo_data.get("asignatura_id")

    asignatura_data = supabase.table("asignatura").select("*").eq("id", asignatura_data_id).single().execute().data
    plan_estudio_data_id = asignatura_data.get("plan_estudio")

    plan_estudio_data = supabase.table("plan_estudio").select("*").eq("id", plan_estudio_data_id).single().execute().data



    # 2. Contenido de la clase
    contenido = supabase.table("clase_contenido").select("*").eq("clase_id", id_clase).execute().data

    # 3. Resultados del estudiante
    resultados = supabase.table("resultados").select("*").eq("estudiante_id", id_estudiante).execute().data

    # 4. Intereses del estudiante
    intereses = supabase.table("intereses_estudiante").select("*").eq("estudiante_id", id_estudiante).execute().data

    # 5. Etapa actual y filtrado de recursos
    etapa_actual = extraer_etapa_actual(contenido)
    recursos_relevantes = filtrar_contenido_por_etapa(contenido, etapa_actual)

    # 🔁 5.1 Generar explicación GPT para cada recurso visual
    recursos_con_explicacion = []
    # for recurso in recursos_relevantes:
    #     if recurso.get("tipo") == "banco_fotos":
    #         try:
    #             explicacion = explicar_imagen_usando_vision(recurso, clase_data)
    #         except Exception as e:
    #             explicacion = f"⚠️ No se pudo generar la explicación: {str(e)}"
    #         recurso["explicacion_gpt"] = explicacion
    #     recursos_con_explicacion.append(recurso)

    # 6. Obtener resultados con info de prueba asociada
    resultados_con_pruebas = []
    for resultado in resultados:
        prueba_id = resultado.get("prueba_id")
        if prueba_id:
            prueba = supabase.table("prueba").select("nombre, curso").eq("id", prueba_id).single().execute().data
            resultados_con_pruebas.append({
                "prueba_id": prueba_id,
                "nombre": prueba.get("nombre") if prueba else None,
                "curso": prueba.get("curso") if prueba else None,
                "puntos": resultado.get("puntos"),
                "respuestas_correctas": resultado.get("respuestas_correctas"),
                "interpretacion": resultado.get("interpretacion")
            })

    # 7. Respuesta final combinada
    return {
        "clase": clase_data,
        "unidad" : unidad_data,
        "modulo" : modulo_data,
        "prueba":asignatura_data,
        "plan_estudio": plan_estudio_data,

        "contenido_completo": contenido,
        "etapa_actual": etapa_actual,
        "recursos_relevantes": recursos_con_explicacion,  # ✅ con explicaciones
        "resultados_estudiante": resultados_con_pruebas,
        "intereses_estudiante": intereses
    }

def extraer_etapa_actual(contenido):
    etapas = [c["etapa"] for c in contenido if c.get("etapa")]
    return etapas[-1] if etapas else None

def filtrar_contenido_por_etapa(contenido, etapa_actual):
    return [c for c in contenido if c.get("etapa") == etapa_actual]
