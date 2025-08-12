from __future__ import annotations
from typing import Optional, Tuple

from ..domain.ports import UserRepository, QuestionRepository, AnswerRepository, AIProvider, VoiceStorage, CodeExecutor, Orchestrator
from ..models import User, Question, Answer


class UserAppService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def get_or_create(self, telegram_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]) -> User:
        user = await self.users.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.users.create(telegram_id, username, first_name, last_name)
        return user

    async def update_level(self, telegram_id: int, level: str) -> Optional[User]:
        return await self.users.update_by_telegram_id(telegram_id, level=level)

    async def update_category(self, telegram_id: int, category: str) -> Optional[User]:
        return await self.users.update_by_telegram_id(telegram_id, category=category)

    async def stats(self, telegram_id: int) -> dict:
        user = await self.users.get_by_telegram_id(telegram_id)
        return await self.users.get_stats(user.id) if user else {}


class QuestionAppService:
    def __init__(self, users: UserRepository, questions: QuestionRepository) -> None:
        self.users = users
        self.questions = questions

    async def get(self, question_id: int) -> Optional[Question]:
        return await self.questions.get_by_id(question_id)

    async def random_for_user(self, telegram_id: int, level: str, category: str) -> Optional[Question]:
        user = await self.users.get_by_telegram_id(telegram_id)
        if not user:
            return None
        q = await self.questions.get_random(level, category, [])
        if q:
            await self.users.update_by_telegram_id(telegram_id, current_question_id=q.id)
        return q

    async def create(self, question: Question) -> Question:
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
        user = await self.users.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        q = await self.questions.get_by_id(question_id)
        if not q:
            raise ValueError("Question not found")
        ans = await self.answers.create(user.id, question_id, text, "text")
        notes = await self.orch.prepare_notes(q.category, user.telegram_id, user.level or "", q.title)
        eval_dict = await self.ai.evaluate(q, text, "text", notes or None)
        await self.answers.set_score(ans.id, eval_dict["score"], eval_dict["feedback"])
        await self.users.update_by_telegram_id(telegram_id, score=user.score + eval_dict["score"], questions_answered=user.questions_answered + 1)
        return ans, eval_dict

    async def answer_voice(self, telegram_id: int, question_id: int, voice_file_id: str, bot_token: str) -> Tuple[Answer, dict]:
        user = await self.users.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        q = await self.questions.get_by_id(question_id)
        if not q:
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
        ans = await self.answers.create(user.id, question_id, text, "voice", voice_file_id)
        notes = await self.orch.prepare_notes(q.category, user.telegram_id, user.level or "", q.title)
        eval_dict = await self.ai.evaluate(q, text, "voice", notes or None)
        await self.answers.set_score(ans.id, eval_dict["score"], eval_dict["feedback"])
        await self.users.update_by_telegram_id(telegram_id, score=user.score + eval_dict["score"], questions_answered=user.questions_answered + 1)
        return ans, eval_dict


class TutorAppService:
    def __init__(self, executor: CodeExecutor) -> None:
        self.executor = executor

    async def run_code(self, code: str, stdin: str = "") -> dict:
        return await self.executor.execute(code, stdin)
