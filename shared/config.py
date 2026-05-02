"""
Shared configuration module — базовые настройки с возможностью расширения.
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class BaseSettings(BaseSettings):
    """Базовые настройки, общие для всех ботов."""
    openrouter_api_key: str
    llm_primary: str = "google/gemini-2.5-flash"
    llm_fallback: str = "meta-llama/llama-3.3-70b-instruct:free"
    secret_key: str = ""
    bot_token: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ExtendedSettings(BaseSettings):
    """Расширенные настройки для monitoring/infrastructure."""
    openrouter_api_key: str
    llm_primary: str = "google/gemini-2.5-flash"
    llm_fallback: str = "meta-llama/llama-3.3-70b-instruct:free"
    secret_key: str
    bot_token: str = ""
    frontend_origins: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    api_base_url: str = "http://localhost:8000/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> BaseSettings:
    """Фабрика настроек — использует EXTENDED=1 для расширенных настроек."""
    if os.getenv("EXTENDED_SETTINGS"):
        return ExtendedSettings()
    return BaseSettings()


# Default instance
settings = get_settings()