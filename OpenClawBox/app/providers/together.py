"""Together AI provider adapter."""
import httpx
from .base import BaseProvider, RateLimit


class TogetherProvider(BaseProvider):
    """Together AI API adapter."""

    BASE_URL = "https://api.together.xyz/v1"

    def __init__(self, api_key: str):
        super().__init__(api_key, "together")
        self.rate_limit = RateLimit(
            rpm=60, tpm=60000, rpd=10000
        )

    async def chat(self, messages: list, model: str, **kwargs) -> dict:
        """Send chat completion to Together."""
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
        """Get available Together models."""
        return [
            {"id": "meta-llama/Llama-3.3-70B-Instruct-Turbo"},
            {"id": "Qwen/Qwen3-32B"},
        ]