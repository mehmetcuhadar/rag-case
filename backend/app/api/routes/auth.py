from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import select
from app.models import RefreshToken
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_dep
from app.core.config import settings
from app.core.security import (
    hash_password, verify_password,
    create_access_token,
    create_refresh_token_value, refresh_token_hash, decode_token
)
from app.repositories.user_repo import UserRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, LogoutRequest

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(db_dep)):
    
    username = payload.username.strip()
    if await UserRepository.get_by_username(db, username):
        raise HTTPException(status_code=409, detail="Username already exists")

    user = await UserRepository.create_user(
        db,
        username=username,
        password_hash=hash_password(payload.password),
    )

    access = create_access_token(sub=str(user.user_id), username=user.username)

    refresh_value = create_refresh_token_value()
    token_id = uuid4()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await RefreshTokenRepository.create(
        db,
        user_id=user.user_id,
        token_id=token_id,
        token_hash=refresh_token_hash(refresh_value),
        expires_at=expires_at,
    )

    return TokenResponse(access_token=access, refresh_token=refresh_value)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(db_dep)):
    username = payload.username.strip()
    user = await UserRepository.get_by_username(db, username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(sub=str(user.user_id), username=user.username)

    refresh_value = create_refresh_token_value()
    token_id = uuid4()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await RefreshTokenRepository.create(
        db,
        user_id=user.user_id,
        token_id=token_id,
        token_hash=refresh_token_hash(refresh_value),
        expires_at=expires_at,
    )

    return TokenResponse(access_token=access, refresh_token=refresh_value)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(db_dep)):
    # We need user_id to validate refresh token. Easiest: encode user_id into refresh? (not desired).
    # So we do: require client to also send access token? (not desired).
    #
    # Better pattern: store refresh token rows by hash only, but you also need to know which user row matches.
    # We'll implement "hash-only lookup" by querying refresh_tokens.token_hash directly.
    #
    # To support that, add an index on token_hash (recommended) and query by hash.

    token_hash = refresh_token_hash(payload.refresh_token)

    res = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow(),
        )
    )
    rt = res.scalar_one_or_none()
    if not rt:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await UserRepository.get_by_id(db, rt.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # optional: rotate refresh token (recommended)
    await RefreshTokenRepository.revoke(db, token_id=rt.token_id)

    new_refresh_value = create_refresh_token_value()
    new_token_id = uuid4()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await RefreshTokenRepository.create(
        db,
        user_id=user.user_id,
        token_id=new_token_id,
        token_hash=refresh_token_hash(new_refresh_value),
        expires_at=expires_at,
    )

    access = create_access_token(sub=str(user.user_id), username=user.username)
    return TokenResponse(access_token=access, refresh_token=new_refresh_value)


@router.post("/logout", status_code=204)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(db_dep)):
    token_hash = refresh_token_hash(payload.refresh_token)

    

    res = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    rt = res.scalar_one_or_none()
    if rt:
        await RefreshTokenRepository.revoke(db, token_id=rt.token_id)

    return None