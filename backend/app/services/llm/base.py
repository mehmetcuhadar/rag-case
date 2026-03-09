from collections.abc import AsyncIterator
from typing import Protocol


class LLMProvider(Protocol):
    async def stream_chat(self, *, model: str, messages: list[dict]) -> AsyncIterator[str]:
        ...