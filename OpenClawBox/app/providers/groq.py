"""Groq provider adapter."""
import httpx
from .base import BaseProvider, RateLimit


class GroqProvider(BaseProvider):
    """Groq API adapter."""

    BASE_URL = "https://api.groq.com/openai/v1"

    # Free tier limits
    FREE_LIMITS = {
        "llama-3.1-8b-instant": {"rpm": 30, "tpm": 6000, "rpd": 14400},
        "llama-3.3-70b-versatile": {"rpm": 30, "tpm": 12000, "rpd": 1000},
        "qwen/qwen3-32b": {"rpm": 60, "tpm": 6000, "rpd": 1000},
        "openai/gpt-oss-120b": {"rpm": 30, "tpm": 8000, "rpd": 1000},
        "openai/gpt-oss-20b": {"rpm": 30, "tpm": 8000, "rpd": 1000},
    }

    def __init__(self, api_key: str):
        super().__init__(api_key, "groq")
        self.rate_limit = RateLimit(
            rpm=30, tpm=6000, rpd=14400
        )

    async def chat(self, messages: list, model: str, **kwargs) -> dict:
        """Send chat completion to Groq."""
        # Map model names
        model_map = {
            "llama-3.1-8b": "llama-3.1-8b-instant",
            "llama-3.3-70b": "llama-3.3-70b-versatile",
            "qwen3-32b": "qwen/qwen3-32b",
        }
        model = model_map.get(model, model)

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
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            self._update_limits(response.headers, model)
            
            return data

    async def get_models(self) -> list:
        """Get available Groq models."""
        return [{"id": m} for m in self.FREE_LIMITS.keys()]