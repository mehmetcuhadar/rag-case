from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    message_id: int
    chat_id: UUID
    role: str
    content: str
    created_at: datetime