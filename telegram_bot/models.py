from pydantic import BaseModel, Field


class Chat(BaseModel):
    first_name: str
    last_name: str = None
    username: str
    id: int
    type: str

class FromUser(BaseModel):
    first_name: str
    last_name: str = None
    username: str
    id: int
    is_bot: bool

class Message(BaseModel):
    chat: Chat
    from_: FromUser = Field(..., alias='from')
    message_id: int
    text: str

class ChatMember(BaseModel):
    status: str
    user: FromUser

class MyChatMember(BaseModel):
    chat: Chat
    date: int
    from_: FromUser = Field(..., alias='from')
    new_chat_member: ChatMember
    old_chat_member: ChatMember

class TelegramMessagePayload(BaseModel):
    my_chat_member: MyChatMember = None
    message: Message = None
    update_id: int

