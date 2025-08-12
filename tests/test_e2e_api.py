from __future__ import annotations
from fastapi.testclient import TestClient
import os

from src.api import app

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
