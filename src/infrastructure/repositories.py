from __future__ import annotations
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import database, User as UserORM, Question as QuestionORM, Answer as AnswerORM
from ..models import User, Question, Answer
from ..domain.ports import UserRepository, QuestionRepository, AnswerRepository


class SqlAlchemyUserRepository(UserRepository):
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return await database.get_user_by_telegram_id(telegram_id)

    async def create(self, telegram_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> User:
        return await database.create_user(telegram_id, username, first_name, last_name)

    async def update_by_telegram_id(self, telegram_id: int, **kwargs) -> Optional[User]:
        return await database.update_user(telegram_id, **kwargs)

    async def get_stats(self, user_id: int) -> Dict[str, Any]:
        return await database.get_user_stats(user_id)


class SqlAlchemyQuestionRepository(QuestionRepository):
    async def get_by_id(self, question_id: int) -> Optional[Question]:
        return await database.get_question_by_id(question_id)

    async def get_random(self, level: str, category: str, exclude_ids: Optional[List[int]] = None) -> Optional[Question]:
        return await database.get_random_question(level, category, exclude_ids or [])

    async def create(self, question: Question) -> Question:
        async with database.get_session() as session:
            session.add(question)
            await session.commit()
            await session.refresh(question)
            return question


class SqlAlchemyAnswerRepository(AnswerRepository):
    async def create(self, user_id: int, question_id: int, answer_text: str, answer_type: str, voice_file_id: Optional[str] = None) -> Answer:
        return await database.create_answer(user_id, question_id, answer_text, answer_type, voice_file_id)

    async def set_score(self, answer_id: int, score: int, feedback: str) -> Optional[Answer]:
        return await database.update_answer_score(answer_id, score, feedback)
