from fastapi import APIRouter
from api.models.Class import Class  # Asegúrate de importar el nuevo modelo Class
from api.services.class_service import ClassService

routes = APIRouter()
# history_service = ClassService('data/history.txt')

@routes.post("/")
async def query_class(class_data: Class):
    # Aquí puedes acceder a class_data.student para obtener información del estudiante
    print(class_data.question)
    # answer = ClassService.answer_question(class_data.question)
    return {
        "student": {
            "name": class_data.student.name,
            "age": class_data.student.age,
            "year": class_data.student.year,
            "email": class_data.student.email,
        },
        "asignature": class_data.asignature,
        "module": class_data.module,
        "topic": class_data.topic,
        "question_number": class_data.question_number,
        "answer": class_data.question_number
    }
