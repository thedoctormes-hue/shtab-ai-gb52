"""FastAPI application with OpenClawBox router."""

import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from app.router import LLMRouter, ProviderInfo
from app.providers.openrouter import OpenRouterAdapter
from app.providers.groq import GroqAdapter
from app.providers.mistral import MistralAdapter
from app.providers.google import GoogleAdapter
from app.providers.together import TogetherAdapter
from app.providers.cohere import CohereAdapter

app = FastAPI(title="OpenClawBox API")


def get_router():
    """Initialize router with all providers."""
    adapters = [
        ProviderInfo(name="groq", adapter=GroqAdapter(), rate_limit_remaining=300),
        ProviderInfo(name="mistral", adapter=MistralAdapter(), rate_limit_remaining=500000),
        ProviderInfo(name="google", adapter=GoogleAdapter(), rate_limit_remaining=15),
        ProviderInfo(name="together", adapter=TogetherAdapter(), rate_limit_remaining=1000000),
        ProviderInfo(name="cohere", adapter=CohereAdapter(), rate_limit_remaining=1000000),
        ProviderInfo(name="openrouter", adapter=OpenRouterAdapter(), rate_limit_remaining=500),
    ]
    return LLMRouter(adapters)


router = get_router()


class ChatRequest(BaseModel):
    model: str = "auto"
    messages: list
    max_tokens: int = 500
    temperature: float = 0.7


class ChatResponse(BaseModel):
    id: str
    model: str
    usage: dict
    choices: list


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        response = await router.route(
            messages=request.messages,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return response.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status():
    return router.get_status()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)