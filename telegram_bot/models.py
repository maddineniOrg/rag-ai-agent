from typing import Optional

from pydantic import BaseModel, Field


class Chat(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    id: int
    type: str

class FromUser(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    id: int
    is_bot: bool

class Document(BaseModel):
    file_id: str
    file_unique_id: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    file_content: Optional[bytes] = None  # To hold the actual file content after download

class Message(BaseModel):
    chat: Chat
    from_: FromUser = Field(..., alias='from')
    message_id: int
    text: Optional[str] = None
    document: Optional[Document] = None

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
    my_chat_member: Optional[MyChatMember] = None
    message: Optional[Message] = None
    update_id: int

class RagResponse(BaseModel):
    answer: str
    session_id: str
    model: str