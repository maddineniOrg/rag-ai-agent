import os

import httpx
from langchain_google_genai._common import GoogleGenerativeAIError

from langchain_rag.rag import LLM
from telegram_bot.api import send_message
from telegram_bot.database import get_session_id, insert_chat_details
from telegram_bot.models import Message, RagResponse

rag_url = os.environ.get("RAG_URL", "http://localhost:8000")


def process_message(message: Message):
    question = message.text
    chat_id = message.chat.id
    try:
        session_id = get_session_id(chat_id)
        response = ask_rag(question, session_id)
        if (response):
            insert_chat_details(chat_id, response.session_id)
            send_message(chat_id, response.answer)
        else:
            message = "Unable to Process your Question, Due to Internal Error"
            send_message(chat_id, message)
    except GoogleGenerativeAIError as e:
        print(e)
        message = e.args[0]
        send_message(chat_id, message)
        return None

def ask_rag(question: str, session_id: str = None) -> RagResponse:
    url = f"{rag_url}/chat"
    payload = {
        "question": question,
        "session_id": session_id if session_id else "",  # send None instead of empty string
        "model": "gemini-2.0-flash-lite"
    }
    with httpx.Client() as client:
        response = client.post(url, json=payload)
        if response.status_code == 200:
            # Map the JSON to RagResponse directly
            rag_response = RagResponse(**response.json())
            return rag_response
        else:
            print(f"Failed to get response from RAG service: {response.text}")
            return None