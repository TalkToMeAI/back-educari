import openai
import faiss
import numpy as np
# from utils import get_embedding, read_text, generate_answer
from api.models.Class  import Class , Student
class ClassService:
    def __init__(self, class_data: Class):
        self.class_asignature = class_data.asignature
        self.class_module = class_data.module
        self.student_name = class_data.student.name
        self.student_age = class_data.student.age
        self.student_year = class_data.student.year
        self.student_email = class_data.student.email
        self.question = class_data.question
        self.topic = class_data.topic
        self.question_number = class_data.question_number
        self.class_sections = self.load_class()
        self.embeddings = self.create_embeddings()
        self.index = self.create_index()


    def load_class(self):
        return "read_text(self.class_path).split"

    def create_embeddings(self):
        return "[get_embedding(section) for section in self.class_sections]"

    def create_index(self):
        # dimension = len(self.embeddings[0])
        # index = faiss.IndexFlatL2(dimension)
        # index.add(np.array(self.embeddings))
        return "index"

    def answer_question(self, question):
        # query_embedding = get_embedding(question)
        # _, indices = self.index.search(np.array([query_embedding]), k=5)
        # relevant_sections = [self.class_sections[i] for i in indices[0]]
        return "generate_answer(question)"
