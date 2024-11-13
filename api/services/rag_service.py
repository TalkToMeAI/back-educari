import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

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

    def query_rag(self, query_text: str, model_name: str = "gpt-3.5-turbo"):
        results = self.db.similarity_search_with_score(query_text, k=5)
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        print(prompt)
        
        openai_model = ChatOpenAI()
        response_text = openai_model.invoke(prompt)

        sources = [doc.metadata.get("id", None) for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        print(formatted_response)
        return response_text


