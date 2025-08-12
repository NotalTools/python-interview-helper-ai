from __future__ import annotations
from functools import lru_cache

from .infrastructure.repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyQuestionRepository,
    SqlAlchemyAnswerRepository,
)
from .infrastructure.ai import DefaultAIProvider
from .infrastructure.executor import PistonExecutor
from .application.services import InterviewAppService


@lru_cache(maxsize=1)
def get_user_repo() -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository()


@lru_cache(maxsize=1)
def get_question_repo() -> SqlAlchemyQuestionRepository:
    return SqlAlchemyQuestionRepository()


@lru_cache(maxsize=1)
def get_answer_repo() -> SqlAlchemyAnswerRepository:
    return SqlAlchemyAnswerRepository()


@lru_cache(maxsize=1)
def get_ai_provider() -> DefaultAIProvider:
    return DefaultAIProvider()


@lru_cache(maxsize=1)
def get_code_executor() -> PistonExecutor:
    return PistonExecutor()


@lru_cache(maxsize=1)
def get_interview_app_service() -> InterviewAppService:
    return InterviewAppService(
        users=get_user_repo(),
        questions=get_question_repo(),
        answers=get_answer_repo(),
        ai=get_ai_provider(),
    )
