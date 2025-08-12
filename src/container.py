from __future__ import annotations
from functools import lru_cache

from .infrastructure.repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyQuestionRepository,
    SqlAlchemyAnswerRepository,
)
from .infrastructure.ai import DefaultAIProvider
from .infrastructure.executor import PistonExecutor
from .infrastructure.voice import TelegramVoiceStorage
from .infrastructure.orchestrator import DefaultOrchestrator
from .application.services import InterviewAppService
from .application.user_services import UserAppService, QuestionAppService, AnswerAppService, TutorAppService


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


@lru_cache(maxsize=1)
def get_user_app_service() -> UserAppService:
    return UserAppService(get_user_repo())


@lru_cache(maxsize=1)
def get_question_app_service() -> QuestionAppService:
    return QuestionAppService(get_user_repo(), get_question_repo())


@lru_cache(maxsize=1)
def get_answer_app_service() -> AnswerAppService:
    return AnswerAppService(
        users=get_user_repo(),
        questions=get_question_repo(),
        answers=get_answer_repo(),
        ai=get_ai_provider(),
        voice=TelegramVoiceStorage(),
        orch=DefaultOrchestrator(),
    )


@lru_cache(maxsize=1)
def get_tutor_app_service() -> TutorAppService:
    return TutorAppService(get_code_executor())
