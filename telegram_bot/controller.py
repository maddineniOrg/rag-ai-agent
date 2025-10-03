from fastapi import APIRouter, Request
from starlette.responses import PlainTextResponse
from telegram_bot.models import TelegramMessagePayload
from telegram_bot.process import process_message

telegram_bot_router = APIRouter()

@telegram_bot_router.post("/telegram/message", response_class=PlainTextResponse)
def handle_message(payload: TelegramMessagePayload):
    if payload and payload.my_chat_member:
        status = payload.my_chat_member.new_chat_member.status
        is_bot = payload.my_chat_member.new_chat_member.user.is_bot
        if is_bot or status == "kicked":
            print("Ignoring bot message or kicked event")
            return "Message Ignored"
    text = payload.message.text
    print(text)
    try:
        process_message(payload.message)
    except Exception as e:
        print(e)
    return "Message Processed"