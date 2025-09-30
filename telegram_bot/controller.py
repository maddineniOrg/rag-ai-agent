from fastapi import APIRouter, Request
from starlette.responses import PlainTextResponse
from telegram_bot.models import TelegramMessagePayload
from telegram_bot.process import process_message

telegram_bot_router = APIRouter()

@telegram_bot_router.post("/telegram/message", response_class=PlainTextResponse)
def handle_message(payload: TelegramMessagePayload):

    test = payload.message.text
    print(test)
    process_message(payload.message)
    return "OK"