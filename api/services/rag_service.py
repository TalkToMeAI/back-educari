import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage  # Importa las clases necesarias

import redis  
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

class RAGQueryHandler:
    def __init__(self, chroma_path: str = CHROMA_PATH, embedding_type: str = "openai"):
        self.chroma_path = chroma_path
        self.embedding_function = self.get_embedding_function(embedding_type)
        # Asegúrate de pasar la función de embeddings al inicializar Chroma
        self.db = Chroma(persist_directory=self.chroma_path, embedding_function=self.embedding_function)

    def get_embedding_function(self, embedding_type: str):
        if embedding_type == "bedrock":
            return BedrockEmbeddings(credentials_profile_name="default", region_name="us-east-1")
        elif embedding_type == "ollama":
            return OllamaEmbeddings()  
        elif embedding_type == "openai":
            return OpenAIEmbeddings()
        else:
            raise ValueError(f"Unknown embedding type: {embedding_type}")

    def query_rag(self, user_id: str, query_text: str, model_name: str = "gpt-3.5-turbo"):
        # Realiza la búsqueda de contexto similar
        results = self.db.similarity_search_with_score(query_text, k=5)
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        # Crea el prompt
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        
        # Define el modelo
        openai_model = ChatOpenAI()
        response_text = openai_model.invoke(prompt)
        
        # Crea el objeto ConversationBufferMemory
        memory = ConversationBufferMemory()
        conversation_chain = ConversationChain(llm=openai_model, memory=memory)
        
        # Recuperar el historial desde Redis
        historial = redis_client.get(user_id)
        if historial:
            historial_data = eval(historial) 
            messages = historial_data["messages"]
            memory.chat_memory.messages = [
                HumanMessage(content=msg["content"]) if msg["type"] == "human" else AIMessage(content=msg["content"]) 
                for msg in messages
            ]
        
        # Añadir el mensaje del usuario a la memoria
        memory.chat_memory.add_user_message(query_text)
        
        # Obtener la respuesta de la IA
        respuesta = conversation_chain.invoke(input=prompt)
        print(respuesta)
        
        # Guardar el historial con los documentos relevantes
        history_with_sources = {
            "messages": [{"type": "human", "content": msg.content} if isinstance(msg, HumanMessage) else {"type": "ai", "content": msg.content} 
                         for msg in memory.chat_memory.messages],
            "sources": [doc.metadata.get("id", None) for doc, _score in results]
        }
        
        redis_client.set(user_id, str(history_with_sources))  # Guardar correctamente en Redis

        # Devolver la respuesta y fuentes
        sources = [doc.metadata.get("id", None) for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        print(formatted_response)
        return response_text