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

    #Traer la calse anterior si es que tiene en su unidad 
    id_estudiante = id_estudiante.strip()

    clase_data = supabase.table("clase").select("*").eq("id", id_clase).single().execute().data

    clase_anterior_result = (
    supabase.rpc("obtener_clase_anterior", {"clase_actual_id": id_clase})
    .execute()
    )

    clase_anterior = clase_anterior_result.data[0] if clase_anterior_result.data else None



    unidad_data_id = clase_data.get("contenido_id")
    unidad_data = supabase.table("unidad").select("*").eq("id", unidad_data_id).single().execute().data

    modulo_data_id = unidad_data.get("modulo_id")
    modulo_data = supabase.table("modulo").select("*").eq("id", modulo_data_id).single().execute().data
    asignatura_data_id = modulo_data.get("asignatura_id")

    asignatura_data = supabase.table("asignatura").select("*").eq("id", asignatura_data_id).single().execute().data
    plan_estudio_data_id = asignatura_data.get("plan_estudio")

    plan_estudio_data = supabase.table("plan_estudio").select("*").eq("id", plan_estudio_data_id).single().execute().data



    contenido = supabase.table("clase_contenido").select("*").eq("clase_id", id_clase).execute().data

    resultados = supabase.table("resultados").select("*").eq("estudiante_id", id_estudiante).execute().data

    intereses = supabase.table("intereses_estudiante").select("*").eq("estudiante_id", id_estudiante).execute().data


    recursos_con_explicacion = []

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

    return {
        "clase": clase_data,
        "unidad" : unidad_data,
        "modulo" : modulo_data,
        "prueba":asignatura_data,
        "plan_estudio": plan_estudio_data,

        "contenido_completo": contenido,
        "recursos_relevantes": recursos_con_explicacion,  # ✅ con explicaciones
        "resultados_estudiante": resultados_con_pruebas,
        "intereses_estudiante": intereses,
        "clase_anterior": clase_anterior,
    }

def extraer_etapa_actual(contenido):
    etapas = [c["etapa"] for c in contenido if c.get("etapa")]
    return etapas[-1] if etapas else None

def filtrar_contenido_por_etapa(contenido, etapa_actual):
    return [c for c in contenido if c.get("etapa") == etapa_actual]
