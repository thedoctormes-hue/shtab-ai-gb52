"""OpenRouter provider adapter."""
import httpx
from .base import BaseProvider, RateLimit


class OpenRouterProvider(BaseProvider):
    """OpenRouter API adapter with :free model support."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, use_free: bool = True):
        super().__init__(api_key, "openrouter")
        self.use_free = use_free
        self.rate_limit = RateLimit(
            rpm=15,  # Conservative for free tier
            tpm=1000,
            rpd=200
        )

    async def chat(self, messages: list, model: str, **kwargs) -> dict:
        """Send chat completion to OpenRouter."""
        if self.use_free and not model.endswith(":free"):
            model = f"{model}:free"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    **kwargs
                },
                timeout=60.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Update rate limits from headers
            self._update_limits(response.headers)
            
            return data

    async def get_models(self) -> list:
        """Get available models, optionally filtering free only."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            
            models = response.json().get("data", [])
            
            if self.use_free:
                return [m for m in models if ":free" in m.get("id", "")]
            
            return [{"id": m["id"]} for m in models]

    def _update_limits(self, headers: dict):
        """Update rate limits from response headers."""
        try:
            if "x-ratelimit-remaining" in headers:
                self.rate_limit.remaining_rpm = int(headers.get("x-ratelimit-remaining", 0))
        except (ValueError, TypeError):
            pass