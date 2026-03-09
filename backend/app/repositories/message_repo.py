from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,asc

from app.models import Message


class MessageRepository:
    @staticmethod
    async def add_message(db: AsyncSession, *, chat_id, role: str, content: str, token_count: int | None = None) -> Message:
        msg = Message(chat_id=chat_id, role=role, content=content, token_count=token_count)
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg

    @staticmethod
    async def get_recent_messages(db: AsyncSession, *, chat_id, limit: int) -> list[Message]:
        # Load newest then reverse to chronological
        res = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        items = list(res.scalars().all())
        items.reverse()
        return items
    
    @staticmethod
    async def list_messages(db, *, chat_id, limit: int = 200):
        res = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(asc(Message.created_at))
            .limit(limit)
        )
        return list(res.scalars().all())