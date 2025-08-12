from __future__ import annotations
from fastapi.testclient import TestClient
import os

from src.api import app

client = TestClient(app)


def test_admin_search_requires_token(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret")
    r = client.get("/admin/questions")
    assert r.status_code == 401


def test_admin_search_with_token(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret")
    r = client.get("/admin/questions", headers={"X-Admin-Token": "secret"})
    # Может быть 200 (если БД доступна) или 500 (если БД не подключена)
    assert r.status_code in (200, 500)
