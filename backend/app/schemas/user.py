from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserUpsert(BaseModel):
    username: str


class UserOut(BaseModel):
    user_id: UUID
    username: str
    created_at: datetime