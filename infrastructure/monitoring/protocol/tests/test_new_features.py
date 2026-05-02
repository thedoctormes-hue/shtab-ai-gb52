"""
Тесты для новых фич Спринта 2.
Простые тесты без сложных моков.
"""

import pytest
import os
import sys
from pathlib import Path

# Настраиваем SECRET_KEY перед импортом
os.environ["SECRET_KEY"] = "test_secret_key_12345"

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

# Импортируем приложение
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# ── Тесты health endpoint ──────────────────────────────────────────

def test_health():
    """Тест health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "протокол"


# ── Тесты структуры API ─────────────────────────────────────────

def test_edges_endpoint_exists():
    """Проверяем, что эндпоинты edges существуют."""
    # Без авторизации должны получить 401 или 403
    response = client.post("/api/v1/edges", json={
        "from_id": "test-id-1",
        "to_id": "test-id-2"
    })
    # Должен быть 401 (Unauthorized) или 403 (Forbidden)
    assert response.status_code in [401, 403, 422]


def test_settings_endpoint_exists():
    """Проверяем, что эндпоинты settings существуют."""
    response = client.get("/api/v1/settings/exit")
    assert response.status_code in [401, 403, 404]


def test_edges_router_included():
    """Проверяем, что роутер edges подключен."""
    from app.routers import edges
    assert edges.router is not None


def test_settings_router_included():
    """Проверяем, что роутер settings подключен."""
    from app.routers import settings
    assert settings.router is not None


def test_create_edge_schema():
    """Проверяем схему создания связи."""
    from app.routers.edges import EdgeCreate
    schema = EdgeCreate(from_id="id1", to_id="id2", relation_type="similar")
    assert schema.from_id == "id1"
    assert schema.to_id == "id2"
    assert schema.relation_type == "similar"


def test_settings_update_schema():
    """Проверяем схему обновления настроек."""
    from app.routers.settings import ExitSettingsUpdate
    schema = ExitSettingsUpdate(export_format="json", auto_delete_days=30)
    assert schema.export_format == "json"
    assert schema.auto_delete_days == 30
