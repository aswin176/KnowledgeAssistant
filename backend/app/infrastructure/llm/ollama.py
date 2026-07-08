"""Ollama LLM service implementation."""

from collections.abc import AsyncGenerator

import httpx

from app.config import Settings
from app.core.interfaces.repositories import LLMService
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaLLMService(LLMService):
    """Local LLM via Ollama."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    async def generate(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self._settings.llm_temperature,
                        "num_predict": self._settings.llm_max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

    async def stream(self, prompt: str, system: str | None = None) -> AsyncGenerator[str, None]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": self._settings.llm_temperature,
                        "num_predict": self._settings.llm_max_tokens,
                    },
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    import json

                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/api/tags")
                return response.status_code == 200
        except Exception as exc:
            logger.warning("ollama_health_check_failed", error=str(exc))
            return False
