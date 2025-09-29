from langchain_google_genai._common import GoogleGenerativeAIError

from langchain_rag.rag import ask_rag
from webex_bot.api_service import send_message
from webex_bot.database import get_session_id, create_room_details


async def process_message(message):
    question = message.text
    roomId = message.roomId
    try:
        session_id = get_session_id(roomId)
        response = ask_rag(question, session_id)
        if (response):
            await send_message(roomId, response)
        else:
            message = "Unable to Process your Question, Due to Internal Error"
            await send_message(roomId, message)
    except GoogleGenerativeAIError as e:
        print(e)
        message = e.args[0]
        await send_message(roomId, message)
        return None



