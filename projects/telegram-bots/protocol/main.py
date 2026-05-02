"""
ПРОТОКОЛ — FastAPI Core
v1.0 | Безумный Доктор
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

from app.database import init_db
from app.routers import fragments, users, patterns, edges, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Протокол API",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # ограничено для безопасности
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(users.router,     prefix="/api/v1/users",     tags=["users"])
app.include_router(fragments.router, prefix="/api/v1/fragments", tags=["fragments"])
app.include_router(patterns.router,  prefix="/api/v1/patterns",  tags=["patterns"])
app.include_router(edges.router,     prefix="/api/v1/edges",     tags=["edges"])
app.include_router(settings.router, prefix="/api/v1/settings",  tags=["settings"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "протокол"}
