"""Google AI Studio provider adapter."""
import httpx
from .base import BaseProvider, RateLimit


class GoogleProvider(BaseProvider):
    """Google Gemini API adapter."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str):
        super().__init__(api_key, "google")
        self.rate_limit = RateLimit(
            rpm=15, tpm=1000000, rpd=1500
        )

    async def chat(self, messages: list, model: str = "gemini-2.0-flash", **kwargs) -> dict:
        """Send chat completion to Google Gemini."""
        # Convert OpenAI format to Google format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/models/{model}:generateContent?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": contents,
                    "generationConfig": {
                        "maxOutputTokens": kwargs.get("max_tokens", 500),
                        "temperature": kwargs.get("temperature", 0.7),
                    }
                },
                timeout=60.0
            )
            response.raise_for_status()
            
            data = response.json()
            self._update_limits(response.headers)
            
            # Convert to OpenAI-like format
            return self._to_openai_format(data)

    async def get_models(self) -> list:
        """Get available Google models."""
        return [
            {"id": "gemini-2.0-flash"},
            {"id": "gemini-2.5-flash"},
            {"id": "gemini-1.5-flash"},
        ]

    def _to_openai_format(self, data: dict) -> dict:
        """Convert Google response to OpenAI format."""
        candidates = data.get("candidates", [])
        if not candidates:
            return {"choices": []}
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text = parts[0].get("text", "") if parts else ""
        
        return {
            "choices": [{
                "message": {"role": "assistant", "content": text},
                "finish_reason": candidates[0].get("finishReason", "stop")
            }]
        }

    def _update_limits(self, headers: dict):
        """Update rate limits from headers."""
        try:
            if "x-ratelimit-remaining" in headers:
                self.rate_limit.remaining_rpm = int(headers.get("x-ratelimit-remaining", 0))
        except (ValueError, TypeError):
            pass