from fastapi import FastAPI,APIRouter
# from api.controllers import products, ingredients,video_tutorial, preparation, recipe

from pydantic import BaseModel

from services.openai_client import OpenAIChatClient

from dotenv import load_dotenv
load_dotenv()

chat_client = OpenAIChatClient()
app = FastAPI()

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = "gpt-4o"
    system_prompt: str | None = "You're a helpful assistant."


routes = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(request: ChatRequest):
    response = chat_client.chat(
        messages=request.messages,
        model=request.model,
        system_prompt=request.system_prompt
    )
    return {"response": response}



# {
#   "messages": [
#     {
#       "role": "user",
#       "content": "Hello, how are you?"
#     }
#   ],
#   "model": "gpt-4o",
#   "system_prompt": "You're a helpful assistant."
# }