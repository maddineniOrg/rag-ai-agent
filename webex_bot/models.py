from typing import List, Optional

from pydantic import BaseModel, Field

class Message(BaseModel):
    id: str
    text: Optional[str] = None
    room_id: str = Field(..., alias='roomId')
    person_id: str = Field(..., alias='personId')
    person_email: str = Field(..., alias='personEmail')
    file_ids: Optional[List[str]] = Field(None, alias='files')

class File(BaseModel):
    id: str
    name: str
    file_type: str = Field(..., alias='fileType')
    file_size: int = Field(..., alias='fileSize')
    content: Optional[bytes] = None  # To hold the actual file content after download
    download_url: str = Field(..., alias='downloadUrl')
    created: str

class Data(BaseModel):
    id: str
    room_id: str = Field(..., alias='roomId')
    person_id: str = Field(..., alias='personId')
    person_email: str = Field(..., alias='personEmail')
    file_ids: Optional[List[str]] = Field(None, alias='files')
    uploaded_files: Optional[List[File]] = None
    message: Optional[Message] = None

class WebexMessagePayload(BaseModel):
    data: Data

class RagResponse(BaseModel):
    answer: str
    session_id: str
    model: str

class Document(BaseModel):
    file_id: str
    file_unique_id: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    file_content: Optional[bytes] = None  # To hold the actual file content after download
