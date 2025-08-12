from __future__ import annotations
from fastapi.testclient import TestClient
import os

from src.api import app
from src.container import get_question_app_service
from fastapi import Depends


class FakeQuestionService:
    async def search(self, level=None, category=None, q=None, limit: int = 20, offset: int = 0):
        return {"items": [], "total": 0, "limit": limit, "offset": offset}

client = TestClient(app)


def test_admin_search_requires_token(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret")
    r = client.get("/admin/questions")
    assert r.status_code == 401


def test_admin_search_with_token(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret")
    # dependency override: стабильный ответ 200 с пустым списком
    app.dependency_overrides[get_question_app_service] = lambda: FakeQuestionService()
    r = client.get("/admin/questions", headers={"X-Admin-Token": "secret"})
    assert r.status_code == 200
    assert r.json()["total"] == 0
    app.dependency_overrides.clear()
