from pydantic import BaseModel
from api.models.Student import Student  

class Class(BaseModel):
    asignature: str  
    module: str      
    student: Student     
    question: str    
    topic: str       
    question_number: int 