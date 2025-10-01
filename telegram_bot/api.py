import os

import httpx
import requests

import dotenv

dotenv.load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }
    with httpx.Client() as client:
        response = client.post(url, params=params)
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message: {response.text}")