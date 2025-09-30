from langchain_google_genai._common import GoogleGenerativeAIError

from langchain_rag.rag import ask_rag
from telegram_bot.api import send_message
from telegram_bot.database import get_session_id
from telegram_bot.models import Message


def process_message(message: Message):
    question = message.text
    chatId = message.chat.id
    try:
        session_id = get_session_id(chatId)
        answer = ask_rag(question, session_id)
        if (answer):
            send_message(chatId, answer)
        else:
            message = "Unable to Process your Question, Due to Internal Error"
            send_message(chatId, message)
    except GoogleGenerativeAIError as e:
        print(e)
        message = e.args[0]
        send_message(chatId, message)
        return None