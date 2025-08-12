from __future__ import annotations
from typing import Protocol, Optional, List, Dict, Any
from datetime import datetime

from ..models import User, Question, Answer


class UserRepository(Protocol):
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        ...

    async def create(self, telegram_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> User:
        ...

    async def update_by_telegram_id(self, telegram_id: int, **kwargs) -> Optional[User]:
        ...

    async def get_stats(self, user_id: int) -> Dict[str, Any]:
        ...


class QuestionRepository(Protocol):
    async def get_by_id(self, question_id: int) -> Optional[Question]:
        ...

    async def get_random(self, level: str, category: str, exclude_ids: Optional[List[int]] = None) -> Optional[Question]:
        ...

    async def create(self, question: Question) -> Question:
        ...


class AnswerRepository(Protocol):
    async def create(self, user_id: int, question_id: int, answer_text: str, answer_type: str, voice_file_id: Optional[str] = None) -> Answer:
        ...

    async def set_score(self, answer_id: int, score: int, feedback: str) -> Optional[Answer]:
        ...


class AIProvider(Protocol):
    async def evaluate(self, question: Question, user_answer: str, answer_type: str = "text", multi_agent_notes: Optional[str] = None) -> Dict[str, Any]:
        ...

    async def transcribe(self, voice_file_path: str) -> str:
        ...


class CodeExecutor(Protocol):
    async def execute(self, code: str, stdin: str = "") -> Dict[str, Any]:
        ...
