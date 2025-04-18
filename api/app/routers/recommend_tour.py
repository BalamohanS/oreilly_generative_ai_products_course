from fastapi import APIRouter
from models import MessageRequest
from services import Services

services = Services()
router = APIRouter()

@router.post("/query/recommend_tour/", tags=["Marketing Bot"])
def query_knowledge_base_with_ai(request: MessageRequest):
    response = services.recommended_tour_chain.invoke(
        {"input": request.message}, config={"callbacks": [services.callback_handler]}
    )
    return {"response": response}