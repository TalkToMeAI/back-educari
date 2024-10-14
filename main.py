from fastapi import FastAPI,APIRouter
# from api.controllers import products, ingredients,video_tutorial, preparation, recipe
app = FastAPI()

# app.include_router(products.routes, prefix="/products")
routes = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "World"}