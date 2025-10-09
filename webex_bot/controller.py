import nest_asyncio
from starlette.responses import PlainTextResponse
from fastapi import Header, Request, APIRouter, BackgroundTasks

from webex_bot.api_service import get_message, delete_message
from webex_bot.database import get_child_message_ids, delete_message_details, get_rag_file_ids
from webex_bot.models import WebexMessagePayload
from webex_bot.process_service import process_message, delete_file_from_rag

webex_bot_router = APIRouter()

@webex_bot_router.post("/webhook/messages", response_class=PlainTextResponse)
def handle_message(
        payload: WebexMessagePayload = None,  # access full request body via Pydantic model
        background_tasks: BackgroundTasks = None
):
    if(payload is None):
        return "Invalid Payload"

    data = payload.data
    message = get_message(data.id)
    print(message)
    if(message is not None and message.person_email.endswith("@webex.bot")):
        print("Ignoring bot message")
        return None
    background_tasks.add_task(process_message, message)
    return "OK"

@webex_bot_router.post("/webhook/deleted/messages", response_class=PlainTextResponse)
async def handle_deleted_message(
        payload: WebexMessagePayload = None,  # access full request body via Pydantic model
):
    if(payload is None):
        return "Invalid Payload"
    message_id = payload.data.id
    print(f"Message Deleted with ID: {message_id}")

    rag_file_ids = get_rag_file_ids(message_id)
    for rag_file_id in rag_file_ids:
        print(f"Deleting RAG File with ID: {rag_file_id}")
        delete_file_from_rag(rag_file_id)

    child_message_ids = get_child_message_ids(message_id)
    for child_message_id in child_message_ids:
        print(f"Deleting Child Message with ID: {child_message_id}")
        delete_message(child_message_id)
        delete_message_details(child_message_id)
    return "OK"



