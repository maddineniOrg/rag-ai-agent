import os

import httpx
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from webex_bot.models import Message
import json

load_dotenv()
BOT_ACCESS_TOKEN= os.getenv("WEBEX_API_KEY")
WEBEX_API_URL = os.getenv("WEBEX_API_URL")

async def get_message(message_id: str):
    """
    Fetch messages from a Webex room using Webex REST API
    """
    headers = {
        "Authorization": f"Bearer {BOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # params = {
    #     "roomId": room_id,
    # }

    WEBEX_MESSAGES_URL = f"{WEBEX_API_URL}/messages/{message_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(WEBEX_MESSAGES_URL, headers=headers)
        if response.status_code == 200:

            payload_bytes = response.content
            payload_str = payload_bytes.decode("utf-8")

            # convert string to dict
            payload_dict = json.loads(payload_str)

            # cast to Pydantic class
            message = Message(**payload_dict)
            return message
        else:
            print("Error fetching the message")
            return None



import httpx
import os

BOT_ACCESS_TOKEN = os.getenv("WEBEX_API_KEY")
WEBEX_API_URL = "https://webexapis.com/v1"

async def send_message(room_id: str, text: str):
    """
    Send a message to a Webex room using Webex REST API
    """
    headers = {
        "Authorization": f"Bearer {BOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "roomId": room_id,
        "markdown": text,
    }

    WEBEX_MESSAGES_URL = f"{WEBEX_API_URL}/messages"
    async with httpx.AsyncClient() as client:
        response = await client.post(WEBEX_MESSAGES_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()   # Webex response (dict with id, roomId, text, etc.)
        else:
            print("Error sending the message:", response.status_code, response.text)
            return None

