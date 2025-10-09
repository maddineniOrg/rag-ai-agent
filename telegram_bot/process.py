import os
import io

import httpx
from langchain_google_genai._common import GoogleGenerativeAIError

from langchain_rag.rag import LLM
from telegram_bot.api import send_message, download_telegram_file
from telegram_bot.database import get_session_id, insert_chat_details
from telegram_bot.models import Message, RagResponse, Document

rag_url = os.environ.get("RAG_URL", "http://localhost:8000")


def process_message(message: Message):
    question = message.text
    chat_id = message.chat.id
    document = message.document
    message_id = message.message_id
    if document:
        file_content = download_telegram_file(document.file_id)
        document.file_content = file_content
        print(f"Downloaded file of size: {len(file_content) if file_content else 'None'} bytes")

        try:
            file_id = upload_file_to_rag(document)
            if file_id:
                reply_message = f"File uploaded successfully. And the assigned file_id is: {file_id}\nYou can now ask questions related to the document."
            else:
                print(f"Failed to upload file to RAG service. Please try again.")
                reply_message = "Failed to upload the file. Please try again."
            send_message(chat_id, reply_message, message_id)
        except TypeError as e:
            print(e)
            reply_message = e.args[0]
            send_message(chat_id, reply_message, message_id)
    elif question:
        if(question.strip().lower().startswith("/delete")):
            file_id = question.split(" ")[1].strip()
            delete_file_from_rag(int(file_id))
            reply_message = f"File deleted successfully with file_id: {file_id}"
            send_message(chat_id, reply_message, message_id)
        else:
            try:
                session_id = get_session_id(chat_id)
                response = ask_rag(question, session_id)
                if response:
                    insert_chat_details(chat_id, response.session_id)
                    send_message(chat_id, response.answer, message_id)
                else:
                    reply_message = "Unable to Process your Question, Due to Internal Error"
                    send_message(chat_id, reply_message, message_id)
            except GoogleGenerativeAIError as e:
                print(e)
                reply_message = e.args[0]
                send_message(chat_id, reply_message, message_id)
                return None
    return None


def ask_rag(question: str, session_id: str = None) -> RagResponse:
    url = f"{rag_url}/chat"
    payload = {
        "question": question,
        "session_id": session_id if session_id else "",
        "model": "gemini-2.0-flash-lite"
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload)
        if response.status_code == 200:
            # Map the JSON to RagResponse directly
            rag_response = RagResponse(**response.json())
            return rag_response
        else:
            print(f"Failed to get response from RAG service: {response.text}")
            return None

def upload_file_to_rag(file: Document) -> str:
    url = f"{rag_url}/upload-doc"
    files = {
        'file': (file.file_name, io.BytesIO(file.file_content), file.mime_type or 'application/octet-stream')
    }
    with httpx.Client() as client:
        response = client.post(url, files=files)
        if response.status_code == 200:
            return response.json().get("file_id")
        else:
            reply_message = f"Failed to upload file to RAG service: {response.text}"
            raise TypeError(reply_message)

def delete_file_from_rag(file_id: str) -> bool:
    url = f"{rag_url}/delete-doc"
    payload = {"file_id": file_id}

    with httpx.Client() as client:
        # use request() so we can send JSON in DELETE
        response = client.request("DELETE", url, json=payload)

        if response.status_code == 200:
            return True
        else:
            print(f"Failed to delete file from RAG service: {response.text}")
            return False
