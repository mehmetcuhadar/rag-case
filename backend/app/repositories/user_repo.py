from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from sqlalchemy.dialects.postgresql import UUID as PGUUID

    


class UserRepository:
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        res = await db.execute(select(User).where(User.username == username))
        return res.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id) -> User | None:
        res = await db.execute(select(User).where(User.user_id == user_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, *, username: str, password_hash: str) -> User:
        user = User(username=username, password_hash=password_hash)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user