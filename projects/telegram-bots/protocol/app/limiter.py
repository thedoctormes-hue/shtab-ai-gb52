"""
Rate limiter for Protocol API.
Shared instance to be used across routers.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],  # глобальный лимит
    storage_uri="memory://",  # in-memory storage, ok for single process
)
