from __future__ import annotations
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update as sa_update, delete as sa_delete, func
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
        async with database.get_session() as session:
            return await session.get(QuestionORM, question_id)

    async def get_random(self, level: str, category: str, exclude_ids: Optional[List[int]] = None) -> Optional[Question]:
        async with database.get_session() as session:
            stmt = select(QuestionORM).where(
                QuestionORM.level == level,
                QuestionORM.category == category,
            )
            if exclude_ids:
                stmt = stmt.where(~QuestionORM.id.in_(exclude_ids))
            stmt = stmt.order_by(QuestionORM.id.desc()).limit(1)
            result = await session.scalars(stmt)
            return result.first()

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
        async with database.get_session() as session:
            stmt = select(QuestionORM)
            if level:
                stmt = stmt.where(QuestionORM.level == level)
            if category:
                stmt = stmt.where(QuestionORM.category == category)
            if q:
                like = f"%{q}%"
                stmt = stmt.where((QuestionORM.title.ilike(like)) | (QuestionORM.content.ilike(like)))
            stmt = stmt.order_by(QuestionORM.id.desc()).limit(limit).offset(offset)
            result = await session.scalars(stmt)
            return list(result.all())

    async def count(self, level: Optional[str] = None, category: Optional[str] = None, q: Optional[str] = None) -> int:
        async with database.get_session() as session:
            stmt = select(func.count(QuestionORM.id))
            if level:
                stmt = stmt.where(QuestionORM.level == level)
            if category:
                stmt = stmt.where(QuestionORM.category == category)
            if q:
                like = f"%{q}%"
                stmt = stmt.where((QuestionORM.title.ilike(like)) | (QuestionORM.content.ilike(like)))
            total = await session.scalar(stmt)
            return int(total or 0)

    async def update(self, question_id: int, data: Dict[str, Any]) -> Optional[Question]:
        async with database.get_session() as session:
            if not data:
                return await session.get(QuestionORM, question_id)
            await session.execute(
                sa_update(QuestionORM).where(QuestionORM.id == question_id).values(**data)
            )
            await session.commit()
            return await session.get(QuestionORM, question_id)

    async def delete(self, question_id: int) -> bool:
        async with database.get_session() as session:
            await session.execute(sa_delete(QuestionORM).where(QuestionORM.id == question_id))
            await session.commit()
            return True


class SqlAlchemyAnswerRepository(AnswerRepository):
    async def create(self, user_id: int, question_id: int, answer_text: str, answer_type: str, voice_file_id: Optional[str] = None) -> Answer:
        return await database.create_answer(user_id, question_id, answer_text, answer_type, voice_file_id)

    async def set_score(self, answer_id: int, score: int, feedback: str) -> Optional[Answer]:
        return await database.update_answer_score(answer_id, score, feedback)
