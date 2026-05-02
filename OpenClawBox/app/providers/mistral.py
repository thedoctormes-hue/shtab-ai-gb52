"""Mistral provider adapter."""
import httpx
from .base import BaseProvider, RateLimit


class MistralProvider(BaseProvider):
    """Mistral AI API adapter."""

    BASE_URL = "https://api.mistral.ai/v1"

    def __init__(self, api_key: str):
        super().__init__(api_key, "mistral")
        self.rate_limit = RateLimit(
            rpm=30, tpm=500000, rpd=5000
        )

    async def chat(self, messages: list, model: str = "mistral-small-latest", **kwargs) -> dict:
        """Send chat completion to Mistral."""
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
            
            return response.json()

    async def get_models(self) -> list:
        """Get available Mistral models."""
        return [
            {"id": "mistral-small-latest"},
            {"id": "mistral-large-latest"},
            {"id": "codestral-latest"},
        ]