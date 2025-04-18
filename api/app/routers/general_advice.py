from fastapi import APIRouter
from models import MessageRequest
from services import Services

services = Services()
router = APIRouter()

@router.post("/query/general_advice/", tags=["Support Ticket Agent"])
def query_general_advice(request: MessageRequest):
    response = services.general_advice_chain.invoke(
        {"question": request.message}, config={"callbacks": [services.callback_handler]}
    )
    return {"response": response}