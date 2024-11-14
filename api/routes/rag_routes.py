from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.rag_service import RAGQueryHandler


routes = APIRouter()

class RAGQuery(BaseModel):
    user_id: str
    question: str
    model: str = "gpt-3.5-turbo"
    embedding: str = "openai"

@routes.post("/rag")
async def rag(rag_query: RAGQuery):
    try:
        print("Entrando al RAG")
        handler = RAGQueryHandler()
        print("Sale del rag")
        response = handler.query_rag(user_id=rag_query.user_id, query_text=rag_query.question, model_name=rag_query.model)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
