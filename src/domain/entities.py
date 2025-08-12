from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..models import Question as DTOQuestion
from ..models import Answer as DTOAnswer
from ..models import User as DTOUser


@dataclass
class UserEntity:
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    level: Optional[str]
    category: Optional[str]
    current_question_id: Optional[int]
    score: int
    questions_answered: int
    created_at: datetime
    updated_at: datetime


def dto_to_user_entity(dto: DTOUser) -> UserEntity:
    return UserEntity(
        id=dto.id,
        telegram_id=dto.telegram_id,
        username=dto.username,
        first_name=dto.first_name,
        last_name=dto.last_name,
        level=dto.level,
        category=dto.category,
        current_question_id=dto.current_question_id,
        score=dto.score,
        questions_answered=dto.questions_answered,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


def entity_to_dto_user(entity: UserEntity) -> DTOUser:
    return DTOUser(
        id=entity.id,
        telegram_id=entity.telegram_id,
        username=entity.username,
        first_name=entity.first_name,
        last_name=entity.last_name,
        level=entity.level,
        category=entity.category,
        current_question_id=entity.current_question_id,
        score=entity.score,
        questions_answered=entity.questions_answered,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


@dataclass
class QuestionEntity:
    id: int
    title: str
    content: str
    level: str
    category: str
    question_type: str
    points: int
    correct_answer: str
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> None:
        if self.level not in {"junior", "middle", "senior"}:
            raise ValueError("invalid level")
        if not self.title or not self.content:
            raise ValueError("empty title/content")
        if self.points <= 0:
            raise ValueError("points must be > 0")


def dto_to_question_entity(dto: DTOQuestion) -> QuestionEntity:
    return QuestionEntity(
        id=dto.id,
        title=dto.title,
        content=dto.content,
        level=dto.level,
        category=dto.category,
        question_type=dto.question_type,
        points=dto.points,
        correct_answer=dto.correct_answer,
        explanation=dto.explanation,
        hints=dto.hints,
        tags=dto.tags,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


def entity_to_dto_question(entity: QuestionEntity) -> DTOQuestion:
    return DTOQuestion(
        id=entity.id,
        title=entity.title,
        content=entity.content,
        level=entity.level,
        category=entity.category,
        question_type=entity.question_type,
        points=entity.points,
        correct_answer=entity.correct_answer,
        explanation=entity.explanation,
        hints=entity.hints,
        tags=entity.tags,
        created_at=entity.created_at or datetime.utcnow(),
        updated_at=entity.updated_at or datetime.utcnow(),
    )


@dataclass
class AnswerEntity:
    id: int
    user_id: int
    question_id: int
    answer_text: str
    answer_type: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    voice_file_id: Optional[str] = None
    created_at: Optional[datetime] = None


def dto_to_answer_entity(dto: DTOAnswer) -> AnswerEntity:
    return AnswerEntity(
        id=dto.id,
        user_id=dto.user_id,
        question_id=dto.question_id,
        answer_text=dto.answer_text,
        answer_type=dto.answer_type,
        score=dto.score,
        feedback=dto.feedback,
        voice_file_id=dto.voice_file_id,
        created_at=dto.created_at,
    )


def entity_to_dto_answer(entity: AnswerEntity) -> DTOAnswer:
    return DTOAnswer(
        id=entity.id,
        user_id=entity.user_id,
        question_id=entity.question_id,
        answer_text=entity.answer_text,
        answer_type=entity.answer_type,
        score=entity.score,
        feedback=entity.feedback,
        voice_file_id=entity.voice_file_id,
        created_at=entity.created_at or datetime.utcnow(),
    )
