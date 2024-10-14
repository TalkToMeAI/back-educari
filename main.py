from fastapi import FastAPI,APIRouter
# from api.controllers import products, ingredients,video_tutorial, preparation, recipe
from api.controllers import class_controler
app = FastAPI()

app.include_router(class_controler.routes, prefix="/class")
routes = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "World"}