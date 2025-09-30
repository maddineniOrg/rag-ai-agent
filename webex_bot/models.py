from typing import List

from pydantic import BaseModel

class Data(BaseModel):
    id: str
    roomId: str
    personId: str
    files: List[str] = []

class WebexMessagePayload(BaseModel):
    data: Data

class Message(BaseModel):
    id: str
    text: str
    roomId: str
    personId: str
    personEmail: str

class File(BaseModel):
    id: str
    fileType: str
    fileSize: int
    content: str
    text: str
    downloadUrl: str
    created: str
