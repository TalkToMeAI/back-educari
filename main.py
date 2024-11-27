from fastapi import FastAPI,APIRouter
from api.routes import class_controler, chroma_routes, rag_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# app.include_router(class_controler.routes, prefix="/class")
app.include_router(chroma_routes.routes, prefix="/db")
app.include_router(rag_routes.routes, prefix="/rag")

routes = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "World"}