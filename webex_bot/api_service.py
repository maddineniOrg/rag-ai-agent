import base64
import datetime
import io
import os
import re
from xml.dom.minidom import Document

import PyPDF2
import httpx

from dotenv import load_dotenv
from webex_bot.models import Message, File

load_dotenv()
WEBEX_BOT_TOKEN= os.getenv("WEBEX_BOT_TOKEN")
WEBEX_API_URL = os.getenv("WEBEX_API_URL")

def get_message(message_id: str):
    """
    Fetch messages from a Webex room using Webex REST API
    """
    headers = {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    # params = {
    #     "roomId": room_id,
    # }

    url = f"{WEBEX_API_URL}/messages/{message_id}"
    with httpx.Client() as client:  # sync client
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            payload_dict = response.json()
            message = Message(**payload_dict)
            return message
        else:
            print(f"Error fetching the message: {response.text}")
            return None

def send_message(room_id: str, text: str):
    """
    Send a message to a Webex room using Webex REST API
    """
    headers = {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "roomId": room_id,
        "markdown": text,
    }

    url = f"{WEBEX_API_URL}/messages"
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()   # Webex response (dict with id, roomId, text, etc.)
        else:
            print("Error sending the message:", response.status_code, response.text)
            return None

def get_files(file_urls: list, save_folder: str = None):
    headers = {"Authorization": f"Bearer {WEBEX_BOT_TOKEN}", "Content-Type": "application/json"}
    files = []

    with httpx.Client() as client:
        for url in file_urls:
            url = url.strip()
            file_id = url.split("/")[-1]
            response = client.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Error fetching file {file_id}: {response.text}")
                continue

            content = response.content
            filename = extract_filename(response.headers, fallback=file_id)
            text = extract_text_from_file(filename, content)
            save_file(content, filename, save_folder)

            file_model = File(
                id=file_id,
                fileType=filename.split('.')[-1],
                fileSize=len(content),
                content=base64.b64encode(content).decode("utf-8"),  # store as base64 string
                text=text or "",
                downloadUrl=url,
                created=datetime.datetime.utcnow().isoformat()
            )

            files.append(file_model)

    return files


def extract_filename(headers, fallback):
    """Extract filename from Content-Disposition header or fallback."""
    cd = headers.get("content-disposition", "")
    match = re.search(r'filename="(.+)"', cd)
    return match.group(1) if match else fallback

def extract_text_from_file(filename, content):
    """Extract text from PDF, DOCX, or TXT if possible."""
    try:
        if filename.lower().endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "".join(page.extract_text() or "" for page in reader.pages)
        elif filename.lower().endswith(".docx"):
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        elif filename.lower().endswith(".txt"):
            return content.decode("utf-8")
    except Exception as e:
        print(f"Could not extract text from {filename}: {e}")
    return None

def save_file(content, filename, folder):
    """Save file to disk if folder is specified."""
    if folder:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        with open(path, "wb") as f:
            f.write(content)
