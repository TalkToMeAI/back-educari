from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.rag_service import RAGQueryHandler


routes = APIRouter()

class RAGQuery(BaseModel):
    user_id: str
    question: str
    model: str = "gpt-3.5-turbo"
    embedding: str = "openai"
    student_name: str
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

@routes.post("/gpt")
async def gpt(rag_query: RAGQuery):
    try:
        handler = RAGQueryHandler()
        response = handler.query_gpt(user_id=rag_query.user_id, student_name=rag_query.student_name, query_text=rag_query.question, model_name=rag_query.model)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@routes.post("/combined")
async def combined(rag_query: RAGQuery):
    try:
        handler = RAGQueryHandler()
        response = handler.query_combined(user_id=rag_query.user_id, query_text=rag_query.question, model_name=rag_query.model)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
