from pydantic import BaseModel

class Data(BaseModel):
    id: str
    roomId: str
    personId: str

class MessagePayload(BaseModel):
    data: Data

class Message(BaseModel):
    id: str
    text: str
    roomId: str
    personId: str
    personEmail: str
