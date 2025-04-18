from fastapi import APIRouter
from models import MessageRequest
from services import Services

services = Services()
router = APIRouter()

@router.post("/query/sql/", tags=["Support Ticket Agent"])
def query_sql(request: MessageRequest):
    response = services.sql_agent_executor.invoke(
        request.message, return_only_outputs=True, config={"callbacks": [services.callback_handler]}
    )["output"]
    return {"response": response}