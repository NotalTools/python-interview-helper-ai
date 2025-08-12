from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..models import Question as DTOQuestion


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
