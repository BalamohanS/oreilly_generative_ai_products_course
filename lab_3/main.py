from fastapi import FastAPI
from pydantic import BaseModel
from langchain.chat_models import init_chat_model

app = FastAPI()
model = init_chat_model("gpt-4o-mini", model_provider="openai")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask")
def get_answer(request: PromptRequest):
    result = model.invoke(request.prompt)
    return {"response": result.content}