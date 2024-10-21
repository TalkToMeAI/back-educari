from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.rag_service import RAGQueryHandler

routes = APIRouter()

class RAGQuery(BaseModel):
    query_text: str
    model: str = "gpt-3.5-turbo"
    embedding: str = "bedrock"

@routes.post("/rag")
async def rag(rag_query: RAGQuery):
    try:
        print("Entrando al RAG")
        handler = RAGQueryHandler()
        print("Sale del rag")
        response = handler.query_rag(query_text=rag_query.query_text, model_name=rag_query.model)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
