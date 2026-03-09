from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import RefreshToken


class RefreshTokenRepository:
    @staticmethod
    async def create(db: AsyncSession, *, user_id, token_id, token_hash: str, expires_at: datetime) -> RefreshToken:
        rt = RefreshToken(user_id=user_id, token_id=token_id, token_hash=token_hash, expires_at=expires_at)
        db.add(rt)
        await db.commit()
        await db.refresh(rt)
        return rt

    @staticmethod
    async def find_valid(db: AsyncSession, *, user_id, token_hash: str) -> RefreshToken | None:
        # valid = matches hash, not revoked, not expired
        res = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def revoke(db: AsyncSession, *, token_id) -> None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_id == token_id)
            .values(revoked_at=datetime.utcnow())
        )
        await db.commit()