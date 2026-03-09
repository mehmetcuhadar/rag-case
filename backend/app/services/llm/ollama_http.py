from collections.abc import AsyncIterator
import json
import httpx


class OllamaHTTP:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    async def chat(
            self,
            *,
            model: str,
            messages: list[dict],
            options: dict | None = None,
        ) -> str:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
            }

            if options:
                payload["options"] = options

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

            return (data.get("message") or {}).get("content") or ""
    
    async def stream_chat(self, *, model: str, messages: list[dict]) -> AsyncIterator[str]:
        url = f"{self.base_url}/api/chat"
        payload = {"model": model, "messages": messages, "stream": True}

        import time
        start = time.time()
        first = True

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()

                async for line in resp.aiter_lines():
                    if not line:
                        continue

                    if first:
                        print("FIRST TOKEN AFTER", round(time.time() - start, 2), "seconds")
                        first = False

                    data = json.loads(line)

                    if data.get("done"):
                        break

                    chunk = (data.get("message") or {}).get("content") or ""
                    if chunk:
                        # Some model configurations return each streamed token as a JSON
                        # string literal (e.g. "\"Title\""), which would surface as
                        # visible quote/escape noise in the UI. Unwrap in that case.
                        if len(chunk) >= 2 and chunk[0] == '"' and chunk[-1] == '"':
                            try:
                                decoded = json.loads(chunk)
                                if isinstance(decoded, str):
                                    chunk = decoded
                            except json.JSONDecodeError:
                                pass
                        yield chunk
