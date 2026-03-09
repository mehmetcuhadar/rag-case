from fastapi import APIRouter
import httpx
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/health/ollama")
async def ollama_health():
    url = f"{settings.OLLAMA_HOST}/api/tags"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
    return {"ollama": "ok", "tags_count": len(r.json().get("models", []))}

@router.post("/debug/ollama-chat")
async def debug_ollama_chat():
    payload = {
        "model": settings.MODEL_NAME,
        "messages": [{"role": "user", "content": "Say hello in one sentence."}],
        "stream": False
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{settings.OLLAMA_HOST}/api/chat", json=payload)
        r.raise_for_status()
    return r.json()