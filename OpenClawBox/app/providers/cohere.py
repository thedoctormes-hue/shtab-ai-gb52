"""Cohere provider adapter."""
import httpx
from .base import BaseProvider, RateLimit


class CohereProvider(BaseProvider):
    """Cohere API adapter."""

    BASE_URL = "https://api.cohere.com/v2"

    def __init__(self, api_key: str):
        super().__init__(api_key, "cohere")
        self.rate_limit = RateLimit(
            rpm=60, tpm=1000000, rpd=10000
        )

    async def chat(self, messages: list, model: str = "command-r", **kwargs) -> dict:
        """Send chat completion to Cohere."""
        # Convert messages to Cohere format
        chat_history = []
        for msg in messages[:-1]:
            role = "USER" if msg["role"] == "user" else "CHATBOT"
            chat_history.append({"role": role, "message": msg["content"]})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/chat",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "chat_history": chat_history,
                    "message": messages[-1]["content"] if messages else "",
                    **{k: v for k, v in kwargs.items() if k != "messages"}
                },
                timeout=60.0
            )
            response.raise_for_status()
            
            return self._to_openai_format(response.json())

    async def get_models(self) -> list:
        """Get available Cohere models."""
        return [
            {"id": "command-r"},
            {"id": "command-r-plus"},
        ]

    def _to_openai_format(self, data: dict) -> dict:
        """Convert Cohere response to OpenAI format."""
        text = data.get("text", "")
        return {
            "choices": [{
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop"
            }]
        }