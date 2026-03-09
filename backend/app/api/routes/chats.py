from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import *
from app.schemas.chat import ChatCreate, ChatOut, ChatUpdate
from app.schemas.message import MessageCreate
from app.services.chat_service import ChatService
from app.repositories.chat_repo import ChatRepository
from app.repositories.user_repo import UserRepository
from app.repositories.message_repo import MessageRepository

import time
from collections import defaultdict, deque
import logging
import json

logger = logging.getLogger(__name__)

## Rate Limiting
WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 5 

_user_hits: dict[str, deque[float]] = defaultdict(deque)

def rate_limit_or_429(user_id: str) -> None:
    now = time.time()
    q = _user_hits[user_id]

    # window dışını temizle
    cutoff = now - WINDOW_SECONDS
    while q and q[0] < cutoff:
        q.popleft()

    if len(q) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    q.append(now)

router = APIRouter(prefix="/v1/chats", tags=["chats"])
svc = ChatService()


@router.post("/create", response_model=ChatOut)
async def create_chat(
    payload: ChatCreate,
    db: AsyncSession = Depends(db_dep),
    current_user=Depends(get_current_user),
):
    chat = await svc.create_chat(db, chat_name=payload.chat_name.strip(), user_id=current_user.user_id)
    return {
        "chat_id": chat.chat_id,
        "chat_name": chat.chat_name,
        "created_at": chat.created_at,
    }

@router.get("/list")
async def list_chats(
    db: AsyncSession = Depends(db_dep),
    current_user=Depends(get_current_user),
    limit: int = Query(100, ge=1, le=200),
):
    chats = await ChatRepository.list_chats_for_user(db, user_id=current_user.user_id, limit=limit)
    return [{"chat_id": c.chat_id, "chat_name": c.chat_name, "created_at": c.created_at} for c in chats]


@router.get("/{chat_id}/messages")
async def get_messages(
    chat_id: UUID,
    db: AsyncSession = Depends(db_dep),
    current_user=Depends(get_current_user),
    limit: int = Query(200, ge=1, le=500),
):
    chat = await ChatRepository.get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Chat not found")

    msgs = await MessageRepository.list_messages(db, chat_id=chat_id, limit=limit)
    return [{"message_id": m.message_id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in msgs]


@router.post("/{chat_id}/messages:stream")
async def stream_message(
    chat_id: UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(db_dep),
    current_user=Depends(get_current_user),
):
    rate_limit_or_429(str(current_user.user_id))
    chat = await ChatRepository.get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Chat not found")

    async def event_gen():
        try:
            async for token in svc.stream_user_message(db, chat_id=chat_id, user_content=payload.content):
                yield f"data: {token}\n\n"
            yield "event: done\ndata: [DONE]\n\n"

        except Exception as e:
            logger.exception("Streaming failed")  # <-- prints full traceback in backend logs
            # send the error string to frontend (dev only)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")

@router.patch("/update/{chat_id}")
async def rename_chat(
    chat_id: UUID, 
    payload: ChatUpdate, 
    db: AsyncSession = Depends(db_dep),
    current_user=Depends(get_current_user),):

    chat = await ChatRepository.get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    updated = await ChatRepository.rename_chat(db, chat_id=chat_id, chat_name=payload.chat_name.strip())
    return {"chat_id": updated.chat_id, "chat_name": updated.chat_name, "created_at": updated.created_at}

@router.delete("/delete/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: UUID, 
    db: AsyncSession = Depends(db_dep),
    current_user=Depends(get_current_user),):

    chat = await ChatRepository.get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    ok = await ChatRepository.delete_chat(db, chat_id=chat_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Chat not found")
    return Response(status_code=204)

@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(db_dep),
    current_user=Depends(get_current_user),
):
    rate_limit_or_429(str(current_user.user_id))

    chat = await ChatRepository.get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        full_text = await svc.send_user_message(
            db,
            chat_id=chat_id,
            user_content=payload.content,
        )
        return {"role": "assistant", "content": full_text}
    except Exception as e:
        logger.exception("Send message failed")
        raise HTTPException(status_code=500, detail=str(e))