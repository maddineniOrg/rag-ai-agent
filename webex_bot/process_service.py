from langchain_google_genai._common import GoogleGenerativeAIError

from langchain_rag.rag import ask_rag
from webex_bot.api_service import send_message
from webex_bot.database import get_session_id


def process_message(message):
    question = message.text
    room_id = message.roomId
    try:
        session_id = get_session_id(room_id)
        answer = ask_rag(question, session_id)
        if answer:
            send_message(room_id, answer)
        else:
            message = "Unable to Process your Question, Due to Internal Error"
            send_message(room_id, message)
    except GoogleGenerativeAIError as e:
        print(e)
        message = e.args[0]
        send_message(room_id, message)
        return None



