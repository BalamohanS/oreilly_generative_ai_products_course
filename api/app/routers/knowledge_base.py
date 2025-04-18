from fastapi import APIRouter
from models import MessageRequest
from services import Services


services = Services()
router = APIRouter()

@router.post("/query/knowledge_base_search/", tags=["Support Ticket Agent"])
def query_knowledge_base(request: MessageRequest):
    response = services.customer_support_retriever.invoke(request.message, config={"callbacks": [services.callback_handler]})
    return {"response": response}

@router.post("/query/knowledge_base_search_with_ai/", tags=["Support Ticket Agent"])
def query_knowledge_base_with_ai(request: MessageRequest):
    # analysis_results = services.pii_analyzer.analyze(text=request.message, entities=["PERSON"], language='en')
    # anonymized_text = services.pii_anonymizer.anonymize(text=request.message, analyzer_results=analysis_results)
    response = services.retrieval_qa_chain.invoke(
        {"input": request.message}, config={"callbacks": [services.callback_handler]}
    )
    return {"response": response}