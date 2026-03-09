from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ChatCreate(BaseModel):
    chat_name: str


class ChatOut(BaseModel):
    chat_id: UUID
    chat_name: str
    created_at: datetime

class ChatUpdate(BaseModel):
    chat_name: str = Field(min_length=1, max_length=100)