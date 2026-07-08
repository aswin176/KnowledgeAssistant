"""Google Gemini LLM service implementation."""

from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import Settings
from app.core.interfaces.repositories import LLMService
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiLLMService(LLMService):
    """Gemini-backed LLM service for chat and summarization."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._base_url = settings.gemini_base_url.rstrip("/")

    async def generate(self, prompt: str, system: str | None = None) -> str:
        if not self._api_key:
            return "Gemini API key is not configured. Please set GEMINI_API_KEY in the backend environment."

        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self._settings.llm_temperature,
                "maxOutputTokens": self._settings.llm_max_tokens,
            },
        }
        if system:
            payload["system_instruction"] = {"parts": [{"text": system}]}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/models/{self._model}:generateContent?key={self._api_key}",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return "".join(part.get("text", "") for part in parts if isinstance(part, dict))

    async def stream(self, prompt: str, system: str | None = None) -> AsyncGenerator[str, None]:
        text = await self.generate(prompt, system=system)
        yield text

    async def health_check(self) -> bool:
        return bool(self._api_key)
