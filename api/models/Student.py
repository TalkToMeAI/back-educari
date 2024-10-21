from pydantic import BaseModel

class Student(BaseModel):
    name: str         
    age: int          
    year: int         
    email: str        