import os

import httpx
import requests

import dotenv

dotenv.load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def send_message(chat_id, text, reply_to_message_id=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_to_message_id:
        params["reply_to_message_id"] = reply_to_message_id

    with httpx.Client() as client:
        response = client.post(url, params=params)
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message: {response.text}")

def download_telegram_file(file_id):
    """
        Download a Telegram file using file_id.
        Returns: file_bytes
    """
    # Step 1: Get the file path
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
    params = {"file_id": file_id}
    with httpx.Client() as client:
        response = client.get(url, params=params)
        if response.status_code != 200:
            print(f"Failed to get file info: {response.text}")
            return None, None
        file_info = response.json()
        if not file_info.get("ok"):
            print(f"Error in response: {file_info}")
            return None, None
        file_path = file_info["result"]["file_path"]
        file_name = os.path.basename(file_path)

    # Step 2: Download the file
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    response = requests.get(file_url)
    if response.status_code != 200:
        print(f"Failed to download file: {response.text}")
        return None, None

    return response.content