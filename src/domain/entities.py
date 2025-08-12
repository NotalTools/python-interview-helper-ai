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
    # Безопасное извлечение атрибутов для случаев, когда dto может быть неполным объектом
    return UserEntity(
        id=getattr(dto, 'id', 0),
        telegram_id=getattr(dto, 'telegram_id', 0),
        username=getattr(dto, 'username', None),
        first_name=getattr(dto, 'first_name', None),
        last_name=getattr(dto, 'last_name', None),
        level=getattr(dto, 'level', None),
        category=getattr(dto, 'category', None),
        current_question_id=getattr(dto, 'current_question_id', None),
        score=getattr(dto, 'score', 0),
        questions_answered=getattr(dto, 'questions_answered', 0),
        created_at=getattr(dto, 'created_at', datetime.utcnow()),
        updated_at=getattr(dto, 'updated_at', datetime.utcnow()),
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
    # Безопасное извлечение атрибутов для случаев, когда dto может быть неполным объектом
    return QuestionEntity(
        id=getattr(dto, 'id', 0),
        title=getattr(dto, 'title', ''),
        content=getattr(dto, 'content', ''),
        level=getattr(dto, 'level', ''),
        category=getattr(dto, 'category', ''),
        question_type=getattr(dto, 'question_type', ''),
        points=getattr(dto, 'points', 0),
        correct_answer=getattr(dto, 'correct_answer', ''),
        explanation=getattr(dto, 'explanation', None),
        hints=getattr(dto, 'hints', None),
        tags=getattr(dto, 'tags', None),
        created_at=getattr(dto, 'created_at', datetime.utcnow()),
        updated_at=getattr(dto, 'updated_at', datetime.utcnow()),
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
    # Безопасное извлечение атрибутов для случаев, когда dto может быть неполным объектом
    return AnswerEntity(
        id=getattr(dto, 'id', 0),
        user_id=getattr(dto, 'user_id', 0),
        question_id=getattr(dto, 'question_id', 0),
        answer_text=getattr(dto, 'answer_text', ''),
        answer_type=getattr(dto, 'answer_type', 'text'),
        score=getattr(dto, 'score', None),
        feedback=getattr(dto, 'feedback', None),
        voice_file_id=getattr(dto, 'voice_file_id', None),
        created_at=getattr(dto, 'created_at', datetime.utcnow()),
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
