from __future__ import annotations
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import database, User as UserORM, Question as QuestionORM, Answer as AnswerORM
from ..models import User, Question, Answer
from ..domain.entities import QuestionEntity, entity_to_dto_question
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

    async def create(self, question: Question | QuestionEntity) -> Question:
        if isinstance(question, QuestionEntity):
            question.validate()
            dto = entity_to_dto_question(question)
        else:
            dto = question
        async with database.get_session() as session:
            session.add(dto)
            await session.commit()
            await session.refresh(dto)
            return dto

    async def search(self, level: Optional[str] = None, category: Optional[str] = None, q: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Question]:
        # Простой MVP SQL
        conditions = ["1=1"]
        params: Dict[str, Any] = {}
        if level:
            conditions.append("level = :level")
            params["level"] = level
        if category:
            conditions.append("category = :category")
            params["category"] = category
        if q:
            conditions.append("(title LIKE :q OR content LIKE :q)")
            params["q"] = f"%{q}%"
        where = " AND ".join(conditions)
        sql = f"SELECT * FROM questions WHERE {where} ORDER BY id DESC LIMIT :limit OFFSET :offset"
        params.update({"limit": limit, "offset": offset})
        async with database.get_session() as session:
            result = await session.execute(sql, params)
            return result.fetchall()  # ORM rows map to model via session config

    async def update(self, question_id: int, data: Dict[str, Any]) -> Optional[Question]:
        if not data:
            return await self.get_by_id(question_id)
        sets = ", ".join([f"{k} = :{k}" for k in data])
        sql = f"UPDATE questions SET {sets} WHERE id = :id"
        async with database.get_session() as session:
            await session.execute(sql, {**data, "id": question_id})
            await session.commit()
            return await self.get_by_id(question_id)

    async def delete(self, question_id: int) -> bool:
        async with database.get_session() as session:
            result = await session.execute("DELETE FROM questions WHERE id = :id", {"id": question_id})
            await session.commit()
            return True


class SqlAlchemyAnswerRepository(AnswerRepository):
    async def create(self, user_id: int, question_id: int, answer_text: str, answer_type: str, voice_file_id: Optional[str] = None) -> Answer:
        return await database.create_answer(user_id, question_id, answer_text, answer_type, voice_file_id)

    async def set_score(self, answer_id: int, score: int, feedback: str) -> Optional[Answer]:
        return await database.update_answer_score(answer_id, score, feedback)
