from __future__ import annotations
from fastapi.testclient import TestClient
from typing import Tuple

from src.api import app
from src.container import get_interview_app_service, get_answer_app_service


class FakeInterviewService:
    async def answer_text(self, user_id: int, question_id: int, text: str) -> Tuple[object, dict]:
        class A: id = 1
        return A(), {"score": 10, "feedback": "ok", "is_correct": True}


class FakeAnswerService:
    async def answer_voice(self, user_id: int, question_id: int, voice_file_id: str, bot_token: str) -> Tuple[object, dict]:
        class A: id = 2
        return A(), {"score": 8, "feedback": "ok-voice", "is_correct": True}


def test_answers_text_override():
    app.dependency_overrides[get_interview_app_service] = lambda: FakeInterviewService()
    client = TestClient(app)
    r = client.post("/answers/text", params={"user_id": 1, "question_id": 2}, json="my answer")
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 10
    app.dependency_overrides.clear()


def test_answers_voice_override():
    app.dependency_overrides[get_answer_app_service] = lambda: FakeAnswerService()
    client = TestClient(app)
    r = client.post("/answers/voice", params={"user_id": 1, "question_id": 2}, json="file_1234567890")
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 8
    app.dependency_overrides.clear()
