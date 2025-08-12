from __future__ import annotations
from typing import Optional, Tuple

from ..domain.ports import UserRepository, QuestionRepository, AnswerRepository, AIProvider, VoiceStorage, CodeExecutor, Orchestrator
from ..models import User, Question, Answer
from ..domain.entities import (
    dto_to_user_entity,
    dto_to_question_entity,
    dto_to_answer_entity,
)


class UserAppService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def get_or_create(self, telegram_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> User:
        user_dto = await self.users.get_by_telegram_id(telegram_id)
        if not user_dto:
            user_dto = await self.users.create(telegram_id, username, first_name, last_name)
        _ = dto_to_user_entity(user_dto)
        return user_dto

    async def update_level(self, telegram_id: int, level: str) -> Optional[User]:
        return await self.users.update_by_telegram_id(telegram_id, level=level)

    async def update_category(self, telegram_id: int, category: str) -> Optional[User]:
        return await self.users.update_by_telegram_id(telegram_id, category=category)

    async def stats(self, telegram_id: int) -> dict:
        user_dto = await self.users.get_by_telegram_id(telegram_id)
        if not user_dto:
            return {}
        # Защита от случая, когда user_dto может быть int или неполным объектом
        user_id = getattr(user_dto, 'id', None) or (user_dto.get('id') if isinstance(user_dto, dict) else None)
        if not user_id:
            return {}
        _ = dto_to_user_entity(user_dto) if user_dto else None
        return await self.users.get_stats(user_id)


class QuestionAppService:
    def __init__(self, users: UserRepository, questions: QuestionRepository) -> None:
        self.users = users
        self.questions = questions

    async def get(self, question_id: int) -> Optional[Question]:
        q_dto = await self.questions.get_by_id(question_id)
        _ = dto_to_question_entity(q_dto) if q_dto else None
        return q_dto

    async def random_for_user(self, telegram_id: int, level: str, category: str) -> Optional[Question]:
        user_dto = await self.users.get_by_telegram_id(telegram_id)
        if not user_dto:
            return None
        _ = dto_to_user_entity(user_dto)
        q_dto = await self.questions.get_random(level, category, [])
        if q_dto:
            # Защита от случая, когда q_dto может быть int или неполным объектом
            q_id = getattr(q_dto, 'id', None) or (q_dto.get('id') if isinstance(q_dto, dict) else q_dto if isinstance(q_dto, int) else None)
            if q_id:
                await self.users.update_by_telegram_id(telegram_id, current_question_id=q_id)
        _ = dto_to_question_entity(q_dto) if q_dto else None
        return q_dto

    async def create(self, question: Question) -> Question:
        # допускаем вход как DTO, валидируем на уровне репозитория при необходимости
        return await self.questions.create(question)

    async def search(self, level: str | None, category: str | None, q: str | None, limit: int = 20, offset: int = 0):
        items = await self.questions.search(level=level, category=category, q=q, limit=limit, offset=offset)
        total = await self.questions.count(level=level, category=category, q=q)
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    async def update(self, question_id: int, data: dict) -> Question | None:
        return await self.questions.update(question_id, data)

    async def delete(self, question_id: int) -> bool:
        return await self.questions.delete(question_id)


class AnswerAppService:
    def __init__(self, users: UserRepository, questions: QuestionRepository, answers: AnswerRepository, ai: AIProvider, voice: VoiceStorage, orch: Orchestrator) -> None:
        self.users = users
        self.questions = questions
        self.answers = answers
        self.ai = ai
        self.voice = voice
        self.orch = orch

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
        _ = dto_to_answer_entity(ans_dto)
        notes = await self.orch.prepare_notes(q_ent.category, user_ent.telegram_id, user_ent.level or "", q_ent.title)
        eval_dict = await self.ai.evaluate(q_dto, text, "text", notes or None)
        await self.answers.set_score(ans_dto.id, eval_dict["score"], eval_dict["feedback"])
        await self.users.update_by_telegram_id(telegram_id, score=user_ent.score + eval_dict["score"], questions_answered=user_ent.questions_answered + 1)
        return ans_dto, eval_dict

    async def answer_voice(self, telegram_id: int, question_id: int, voice_file_id: str, bot_token: str) -> Tuple[Answer, dict]:
        user_dto = await self.users.get_by_telegram_id(telegram_id)
        if not user_dto:
            raise ValueError("User not found")
        q_dto = await self.questions.get_by_id(question_id)
        if not q_dto:
            raise ValueError("Question not found")
        ogg_path = f"temp/{voice_file_id}.ogg"
        wav_path = f"temp/{voice_file_id}.wav"
        ok = await self.voice.download_voice(voice_file_id, bot_token, ogg_path)
        if not ok:
            raise ValueError("Failed to download voice")
        ok = await self.voice.convert_ogg_to_wav(ogg_path, wav_path)
        if not ok:
            await self.voice.cleanup(ogg_path)
            raise ValueError("Failed to convert voice")
        from ..infrastructure.ai import DefaultAIProvider
        transcriber = DefaultAIProvider()
        text = await transcriber.transcribe(wav_path)
        await self.voice.cleanup(ogg_path, wav_path)
        if not text:
            raise ValueError("Transcription failed")
        user_ent = dto_to_user_entity(user_dto)
        q_ent = dto_to_question_entity(q_dto)
        ans_dto = await self.answers.create(user_ent.id, question_id, text, "voice", voice_file_id)
        _ = dto_to_answer_entity(ans_dto)
        notes = await self.orch.prepare_notes(q_ent.category, user_ent.telegram_id, user_ent.level or "", q_ent.title)
        eval_dict = await self.ai.evaluate(q_dto, text, "voice", notes or None)
        await self.answers.set_score(ans_dto.id, eval_dict["score"], eval_dict["feedback"])
        await self.users.update_by_telegram_id(telegram_id, score=user_ent.score + eval_dict["score"], questions_answered=user_ent.questions_answered + 1)
        return ans_dto, eval_dict


class TutorAppService:
    def __init__(self, executor: CodeExecutor) -> None:
        self.executor = executor

    async def run_code(self, code: str, stdin: str = "") -> dict:
        return await self.executor.execute(code, stdin)
