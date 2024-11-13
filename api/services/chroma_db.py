import argparse
import os
import shutil
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.vectorstores.chroma import Chroma
from api.services.rag_service import RAGQueryHandler 

class DocumentDatabaseManager:
    def __init__(self, chroma_path="chroma", data_path="data/class/math/number_operation/content/2", embedding_type="openai"):
        self.CHROMA_PATH = chroma_path
        self.DATA_PATH = data_path
        self.embedding_type = embedding_type

        self.rag_handler = RAGQueryHandler(embedding_type=self.embedding_type)

    def main(self, reset=False):
        if reset:
            print("✨ Clearing Database")
            self.clear_database()

        documents = self.load_documents()
        chunks = self.split_documents(documents)
        self.add_to_chroma(chunks)

    def load_documents(self):
        document_loader = PyPDFDirectoryLoader(self.DATA_PATH)
        return document_loader.load()

    def split_documents(self, documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=80,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)

    def add_to_chroma(self, chunks: list[Document]):
        embedding_function = self.rag_handler.get_embedding_function(self.embedding_type)
        
        db = Chroma(
            persist_directory=self.CHROMA_PATH, embedding_function=embedding_function
        )

        chunks_with_ids = self.calculate_chunk_ids(chunks)

        existing_items = db.get(include=[]) 
        existing_ids = set(existing_items["ids"])
        print(f"Number of existing documents in DB: {len(existing_ids)}")

        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["id"] not in existing_ids:
                new_chunks.append(chunk)

        if len(new_chunks):
            print(f"👉 Adding new documents: {len(new_chunks)}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            db.add_documents(new_chunks, ids=new_chunk_ids)
            db.persist()
        else:
            print("✅ No new documents to add")

    def calculate_chunk_ids(self, chunks):

        last_page_id = None
        current_chunk_index = 0

        for chunk in chunks:
            source = chunk.metadata.get("source")
            page = chunk.metadata.get("page")
            current_page_id = f"{source}:{page}"

            if current_page_id == last_page_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0

            chunk_id = f"{current_page_id}:{current_chunk_index}"
            last_page_id = current_page_id

            chunk.metadata["id"] = chunk_id

        return chunks

    def clear_database(self):
        if os.path.exists(self.CHROMA_PATH):
            shutil.rmtree(self.CHROMA_PATH)

