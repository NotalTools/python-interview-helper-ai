from __future__ import annotations
from fastapi.testclient import TestClient
import os

from src.api import app
from src.rate_limit import limiter

client = TestClient(app)


def test_rate_limit_429(monkeypatch):
    # Установим низкий лимит
    limiter.limit = 1
    # Первый вызов — ок
    r1 = client.post("/answers/text", params={"user_id": 7, "question_id": 1}, json="abc")
    # Второй вызов — 429
    r2 = client.post("/answers/text", params={"user_id": 7, "question_id": 1}, json="abc")
    assert r2.status_code == 429
