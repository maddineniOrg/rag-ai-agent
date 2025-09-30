from pydantic import BaseModel, Field


class Chat(BaseModel):
    first_name: str
    last_name: str
    username: str
    id: int
    type: str

class FromUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    id: int
    is_bot: bool

class Message(BaseModel):
    chat: Chat
    from_: FromUser = Field(..., alias='from')
    message_id: int
    text: str

class TelegramMessagePayload(BaseModel):
    message: Message
    update_id: int

