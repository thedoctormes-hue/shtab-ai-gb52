import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

ROLE_STT_MODELS = ["google/gemini-2.5-flash-lite"]

ROLE_CLEAN_MODELS = ["mistralai/mistral-nemo"]

ROLE_PROTOCOL_MODELS = ["mistralai/mistral-nemo", "stepfun/step-3.5-flash"]

ROLE_BACKUP_MODELS = ["google/gemini-2.5-flash-lite", "mistralai/mistral-nemo"]

# Telegram Bot API limit: 20MB max for file download
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_RETRIES_PER_MODEL = 2
RETRY_DELAY = 2

PROMPTS_DIR = BASE_DIR / "prompts"

def load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def validate_config() -> bool:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in .env")
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in .env")
    return True