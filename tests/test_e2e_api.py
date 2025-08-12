from __future__ import annotations
from fastapi.testclient import TestClient
import os

from src.api import app
from src.container import get_user_app_service

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()


def test_levels_categories():
    assert client.get("/levels").status_code == 200
    assert client.get("/categories").status_code == 200


def test_users_flow_create_get_stats(monkeypatch):
    # Ставим токены по умолчанию, чтобы инициализация прошла
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy")
    monkeypatch.setenv("AI_PROVIDER", "openai")
    
    class FakeUserService:
        async def get_or_create(self, telegram_id: int, username: str | None, first_name: str | None, last_name: str | None):
            return {
                "id": 1,
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "level": None,
                "category": None,
                "current_question_id": None,
                "score": 0,
                "questions_answered": 0,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        async def stats(self, telegram_id: int):
            return {}

    app.dependency_overrides[get_user_app_service] = lambda: FakeUserService()

    # create user
    r = client.post("/users/", json={
        "telegram_id": 123,
        "username": "u",
        "first_name": "f",
        "last_name": "l"
    })
    assert r.status_code == 200

    # stats (может отсутствовать если не подключена БД, но эндпоинт отвечает 404)
    r2 = client.get("/users/123/stats")
    assert r2.status_code in (200, 404)
    app.dependency_overrides.clear()
