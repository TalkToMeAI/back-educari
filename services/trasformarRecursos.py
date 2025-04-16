from typing import List






def transformar_contenido_a_recursos(contenido_completo: List[dict]) -> List[dict]:
    recursos = []
    for item in contenido_completo:
        etapa_original = item.get("etapa", "").lower()
        if "introduccion" in etapa_original:
            etapa = "introduccion"
        elif "repaso" in etapa_original:
            etapa = "repaso"
        elif "desarrollo" in etapa_original:
            etapa = "desarrollo"
        elif "ejemplos" in etapa_original:
            etapa = "ejemplos"
        elif "ejercicios" in etapa_original:
            etapa = "ejercicios"
        elif "retroalimentacion" in etapa_original:
            etapa = "retroalimentacion"
        elif "resumen" in etapa_original or "sintesis" in etapa_original:
            etapa = "sintesis"
        else:
            etapa = "desarrollo"

        recurso = {
            "tipo": "imagen" if item.get("tipo") == "banco_fotos" else item.get("tipo"),
            "descripcion": item.get("descripcion", "Recurso sin descripción"),
            "etapa_uso": etapa,
            "url": item.get("data")
        }
        recursos.append(recurso)
    return recursos
