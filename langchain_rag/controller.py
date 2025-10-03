from fastapi import APIRouter
from starlette.responses import PlainTextResponse

from langchain_rag.rag import LLM

rag_router = APIRouter()
llm = LLM()


# chat endpoint
@rag_router.post("/rag/chat", response_class=PlainTextResponse)
def chat_with_rag(question: str, chat_model: str = "", session_id: str = ""):
    response = llm.ask_rag(question)
    return response