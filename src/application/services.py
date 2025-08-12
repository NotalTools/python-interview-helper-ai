from __future__ import annotations
from typing import Optional, Tuple

from ..domain.ports import UserRepository, QuestionRepository, AnswerRepository, AIProvider, DocsProvider
from ..domain.entities import (
    dto_to_user_entity,
    dto_to_question_entity,
    dto_to_answer_entity,
)
from ..interview_service import InterviewService
from ..models import Answer, Question


class InterviewAppService:
    def __init__(self, users: UserRepository, questions: QuestionRepository, answers: AnswerRepository, ai: AIProvider, docs: DocsProvider | None = None) -> None:
        self.users = users
        self.questions = questions
        self.answers = answers
        self.ai = ai
        self.docs = docs

    async def next_question(self, telegram_id: int, level: str, category: str) -> Optional[Question]:
        user_dto = await self.users.get_by_telegram_id(telegram_id)
        if not user_dto:
            raise ValueError("User not found")
        _user = dto_to_user_entity(user_dto)
        q_dto = await self.questions.get_random(level, category, [])
        if q_dto:
            await self.users.update_by_telegram_id(telegram_id, current_question_id=q_dto.id)
        return q_dto

    async def answer_text(self, telegram_id: int, question_id: int, text: str) -> Tuple[Answer, dict]:
        user_dto = await self.users.get_by_telegram_id(telegram_id)
        if not user_dto:
            raise ValueError("User not found")
        q_dto = await self.questions.get_by_id(question_id)
        if not q_dto:
            raise ValueError("Question not found")
        user_ent = dto_to_user_entity(user_dto)
        q_ent = dto_to_question_entity(q_dto)
        ans_dto = await self.answers.create(user_ent.id, question_id, text, "text")
        _ans = dto_to_answer_entity(ans_dto)
        notes = await InterviewService.prepare_expert_notes(q_ent.category, user_ent.telegram_id, user_ent.level or "", q_ent.title)
        # Context7 docs: опционально добавим выдержку для backend категорий
        docs_text = ""
        if self.docs and q.category in {"backend", "databases", "networking", "security"}:
            # пример маппинга: backend -> /python-telegram-bot/python-telegram-bot или /tiangolo/fastapi
            lib = "/tiangolo/fastapi" if q.category == "backend" else "/sqlalchemy/sqlalchemy"
            docs_text = await self.docs.get_docs(library_id=lib, topic=q.title, tokens=1000) or ""
        merged_notes = (notes + "\n\nДокументация:\n" + docs_text) if docs_text else notes
        eval_dict = await self.ai.evaluate(q_dto, text, "text", merged_notes or None)
        await self.answers.set_score(ans_dto.id, eval_dict["score"], eval_dict["feedback"])
        await self.users.update_by_telegram_id(
            telegram_id,
            score=user_ent.score + eval_dict["score"],
            questions_answered=user_ent.questions_answered + 1,
        )
        return ans_dto, eval_dict
