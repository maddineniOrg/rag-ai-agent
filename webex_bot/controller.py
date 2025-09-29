import nest_asyncio
from fastapi import APIRouter
from starlette.responses import PlainTextResponse
from fastapi import FastAPI, Header, Path, Request, APIRouter
import json

from webex_bot.api_service import get_message
from webex_bot.models import MessagePayload
from webex_bot.process_service import process_message

nest_asyncio.apply()

webex_bot_router = APIRouter()

@webex_bot_router.post("/webhook/messages", response_class=PlainTextResponse)
async def handle_webhook_event(
        #botName: str = Path(...),  # path variable
        request: Request = None,  # access full request
        x_spark_signature: str = Header(None)  # request header
):

    message_id = await extract_message_id(request)
    message = await get_message(message_id)
    print(message)
    if(message.personEmail.endswith("@webex.bot")):
        return None
    await process_message(message)
    return "OK"


async def extract_message_id(request: Request, x_spark_signature: str = Header(None)):
    # read raw payload
    payload_bytes = await request.body()
    payload_str = payload_bytes.decode("utf-8")

    # convert string to dict
    payload_dict = json.loads(payload_str)

    # cast to Pydantic class
    payload_obj = MessagePayload(**payload_dict)

    # now you can access fields
    message_id = payload_obj.data.id
    return message_id



