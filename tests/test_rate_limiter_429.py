from __future__ import annotations
from fastapi.testclient import TestClient
import os

from src.api import app
from src.container import get_interview_app_service
from src.rate_limit import limiter

client = TestClient(app)


def test_rate_limit_429(monkeypatch):
    # Установим низкий лимит
    limiter.limit = 1
    # Заглушим сервис, чтобы не трогать БД
    class FakeInterviewService:
        async def answer_text(self, user_id: int, question_id: int, text: str):
            # вернем фейк-ответ
            class A: id = 99
            return A(), {"score": 1, "feedback": "", "is_correct": True}
    app.dependency_overrides[get_interview_app_service] = lambda: FakeInterviewService()
    # Первый вызов — ок
    r1 = client.post("/answers/text", params={"user_id": 7, "question_id": 1}, json="abc")
    # Второй вызов — 429
    r2 = client.post("/answers/text", params={"user_id": 7, "question_id": 1}, json="abc")
    assert r2.status_code == 429
    app.dependency_overrides.clear()
