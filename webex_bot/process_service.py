import io
import os

import httpx
from langchain_google_genai._common import GoogleGenerativeAIError

from webex_bot.api_service import send_message, get_files
from webex_bot.database import get_session_id, insert_room_details, insert_message_details, insert_file_details
from webex_bot.models import RagResponse, File, Message
from webex_bot.models import Data

rag_url = os.getenv("RAG_URL", "http://localhost:8000")


def process_message(message: Message):
    room_id = message.room_id
    file_ids = message.file_ids
    if file_ids and len(file_ids) > 0:
        files = get_files(file_ids)
        print(f"Received {len(files)} files.")
        reply_message = "Files uploaded successfully with file IDs:\n"
        for file in files:
            file_id = upload_file_to_rag(file)
            insert_file_details(file_id, file.id, message.id)
            print(f"Uploaded file with ID: {file_id}")
            reply_message += f"File ID: {file_id} : {file.name}\n"
        reply_message += "You can now ask questions related to the documents."
        child_message_id = send_message(room_id, reply_message, message.id)
        insert_message_details(child_message_id, message.id)
    if message:
        question = message.text
        try:
            session_id = get_session_id(room_id)
            rag_response = ask_rag(question, session_id)
            if rag_response:
                insert_room_details(room_id, rag_response.session_id)
                child_message_id = send_message(room_id, rag_response.answer)
            else:
                message = "Unable to Process your Question, Due to Internal Error"
                send_message(room_id, message)
        except GoogleGenerativeAIError as e:
            print(e)
            message = e.args[0]
            send_message(room_id, message)
            return None

def ask_rag(question: str, session_id: str = None) -> RagResponse:
    url = f"{rag_url}/chat"
    payload = {
        "question": question,
        "session_id": session_id if session_id else "",  # send None instead of empty string
        "model": "gemini-2.0-flash-lite"
    }
    with httpx.Client(timeout=50) as client:
        response = client.post(url, json=payload)
        if response.status_code == 200:
            # Map the JSON to RagResponse directly
            rag_response = RagResponse(**response.json())
            return rag_response
        else:
            print(f"Failed to get response from RAG service: {response.text}")
            return None

def upload_file_to_rag(file: File) -> str:
    url = f"{rag_url}/upload-doc"
    files = {
        'file': (file.name, file.content, f"application/{file.file_type}")
    }
    with httpx.Client(timeout=30) as client:
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



