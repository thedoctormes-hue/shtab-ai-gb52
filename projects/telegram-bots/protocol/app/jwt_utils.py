"""
JWT utilities for Protocol API.
Uses SECRET_KEY from config.py.
"""
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.config import settings


def create_access_token(tg_id: str, user_id: str = None, expires_days: int = 30) -> str:
    """Create JWT access token."""
    payload = {
        "tg_id": tg_id,
        "exp": datetime.utcnow() + timedelta(days=expires_days),
        "iat": datetime.utcnow(),
    }
    if user_id:
        payload["user_id"] = user_id
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
