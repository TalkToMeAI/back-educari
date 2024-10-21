from fastapi import APIRouter, HTTPException
from api.services.chroma_db import DocumentDatabaseManager

routes = APIRouter()

db_manager = DocumentDatabaseManager()

@routes.post("/load-documents")
async def load_documents(reset: bool = False):
    """
    Carga documentos desde la ruta especificada y genera embeddings.
    """
    try:
        db_manager.main(reset=reset)  # Carga y genera embeddings
        return {"message": "Documents loaded and embeddings created.", "reset": reset}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@routes.delete("/clear-database")
async def clear_database():
    """
    Limpia la base de datos de Chroma.
    """
    try:
        db_manager.clear_database()
        return {"message": "Database cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @routes.get("/document-count")
# async def get_document_count():
#     """
#     Retorna el número de documentos en la base de datos.
#     """
#     try:
#         db_manager.main()  # Carga documentos para contar, pero no los agrega
#         document_count = len(db_manager.db.get(include=[]))  # Obtén el conteo de documentos
#         return {"document_count": document_count}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
