from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,desc,update,delete

from app.models import Chat


class ChatRepository:
    @staticmethod
    async def create_chat(db: AsyncSession, *, chat_name: str, user_id) -> Chat:
        chat = Chat(chat_name=chat_name, user_id=user_id)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    @staticmethod
    async def get_chat(db: AsyncSession, chat_id) -> Chat | None:
        res = await db.execute(select(Chat).where(Chat.chat_id == chat_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def list_chats_for_user(db: AsyncSession, user_id, limit):
        res = await db.execute(select(Chat)
                               .where(Chat.user_id == user_id)
                               .order_by(desc(Chat.created_at))
                               .limit(limit))
        return list(res.scalars().all())
    
    @staticmethod
    async def rename_chat(db, *, chat_id, chat_name: str):
        await db.execute(
            update(Chat)
            .where(Chat.chat_id == chat_id)
            .values(chat_name=chat_name)
        )
        await db.commit()

        res = await db.execute(select(Chat).where(Chat.chat_id == chat_id))
        return res.scalar_one_or_none()
    
    @staticmethod
    async def delete_chat(db, *, chat_id) -> bool:
        res = await db.execute(delete(Chat).where(Chat.chat_id == chat_id))
        await db.commit()
        return res.rowcount > 0