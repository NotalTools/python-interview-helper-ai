from __future__ import annotations
from typing import Optional, Tuple

from ..domain.ports import UserRepository, QuestionRepository, AnswerRepository, AIProvider
from ..interview_service import InterviewService
from ..models import Answer, Question


class InterviewAppService:
    def __init__(self, users: UserRepository, questions: QuestionRepository, answers: AnswerRepository, ai: AIProvider) -> None:
        self.users = users
        self.questions = questions
        self.answers = answers
        self.ai = ai

    async def next_question(self, telegram_id: int, level: str, category: str) -> Optional[Question]:
        user = await self.users.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        q = await self.questions.get_random(level, category, [])
        if q:
            await self.users.update_by_telegram_id(telegram_id, current_question_id=q.id)
        return q

    async def answer_text(self, telegram_id: int, question_id: int, text: str) -> Tuple[Answer, dict]:
        user = await self.users.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        q = await self.questions.get_by_id(question_id)
        if not q:
            raise ValueError("Question not found")
        ans = await self.answers.create(user.id, question_id, text, "text")
        notes = await InterviewService.prepare_expert_notes(q.category, user.telegram_id, user.level or "", q.title)
        eval_dict = await self.ai.evaluate(q, text, "text", notes or None)
        await self.answers.set_score(ans.id, eval_dict["score"], eval_dict["feedback"])
        await self.users.update_by_telegram_id(telegram_id, score=user.score + eval_dict["score"], questions_answered=user.questions_answered + 1)
        return ans, eval_dict
