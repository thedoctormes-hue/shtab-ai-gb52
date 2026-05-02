"""
Rate limiter for Protocol API with proxy support.
Reads X-Forwarded-For or X-Real-IP if behind a proxy.
"""
from slowapi import Limiter
from starlette.requests import Request

def get_client_ip(request: Request) -> str:
    """Get real IP, respecting proxy headers."""
    # Проверяем стандартные заголовки прокси
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Берем первый IP из списка (реальный клиент)
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Фолбэк на прямой IP
    return request.client.host

limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["100 per minute"], # глобальный лимит
    storage_uri="memory://",  # in-memory storage, ok for single process
)
