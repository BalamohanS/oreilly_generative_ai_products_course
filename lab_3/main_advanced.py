from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from typing import Dict

app = FastAPI()

# Setup model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Define prompt with placeholder for memory
prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Create base runnable
chain: Runnable = prompt | model

# Simple in-memory store (can be swapped with Redis or DB-backed session memory)
store: Dict[str, ChatMessageHistory] = {}

# Memory-backed chain
memory_chain = RunnableWithMessageHistory(
    chain,
    lambda session_id: store.setdefault(session_id, ChatMessageHistory()),
    input_messages_key="input",
    history_messages_key="history"
)

# Request model
class PromptRequest(BaseModel):
    prompt: str
    session_id: str  # unique ID to identify the user's session

@app.post("/ask")
def ask(request: PromptRequest):
    response = memory_chain.invoke(
        {"input": request.prompt},
        config={"configurable": {"session_id": request.session_id}}
    )
    return {"response": response.content}