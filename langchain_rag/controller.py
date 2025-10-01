from fastapi import APIRouter
from starlette.responses import PlainTextResponse

from langchain_rag.rag import ask_rag

rag_router = APIRouter()


# chat endpoint
@rag_router.post("/rag/chat", response_class=PlainTextResponse)
def chat_with_rag(question: str, chat_model: str = "", session_id: str = ""):
    chat_history = []
    response = ask_rag(question)
    return response