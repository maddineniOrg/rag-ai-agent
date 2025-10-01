import nest_asyncio
from starlette.responses import PlainTextResponse
from fastapi import Header, Request, APIRouter

from webex_bot.api_service import get_message, get_files
from webex_bot.models import WebexMessagePayload
from webex_bot.process_service import process_message

webex_bot_router = APIRouter()

@webex_bot_router.post("/webhook/messages", response_class=PlainTextResponse)
def handle_message(
        payload: WebexMessagePayload = None,  # access full request body via Pydantic model
):
    if(payload is None):
        return "Invalid Payload"
    message = get_message(payload.data.id)
    print(message)
    if(message.personEmail.endswith("@webex.bot")):
        return None
    process_message(message)
    return "OK"



