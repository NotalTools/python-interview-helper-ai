from __future__ import annotations
import pytest
from datetime import datetime

from src.application.user_services import AnswerAppService
from src.domain.ports import UserRepository, QuestionRepository, AnswerRepository, AIProvider, VoiceStorage, Orchestrator
from src.models import User as DTOUser, Question as DTOQuestion, Answer as DTOAnswer


class FakeUserRepo(UserRepository):
    def __init__(self):
        self.users: dict[int, DTOUser] = {}

    async def get_by_telegram_id(self, telegram_id: int):
        return self.users.get(telegram_id)

    async def create(self, telegram_id: int, username, first_name, last_name):
        user = DTOUser(
            id=len(self.users) + 1,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            level="middle",
            category="backend",
            current_question_id=None,
            score=0,
            questions_answered=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.users[telegram_id] = user
        return user

    async def update_by_telegram_id(self, telegram_id: int, **kwargs):
        u = self.users[telegram_id]
        updated = u.model_copy(update=kwargs | {"updated_at": datetime.utcnow()})
        self.users[telegram_id] = updated
        return updated

    async def get_stats(self, user_id: int):
        # find by id
        for u in self.users.values():
            if u.id == user_id:
                avg = (u.score / u.questions_answered) if u.questions_answered else 0
                return {
                    "user_id": user_id,
                    "total_score": u.score,
                    "questions_answered": u.questions_answered,
                    "average_score": avg,
                    "level": u.level,
                    "category": u.category,
                    "last_activity": u.updated_at,
                }
        return {}


class FakeQuestionRepo(QuestionRepository):
    def __init__(self):
        self.questions: dict[int, DTOQuestion] = {}

    async def get_by_id(self, question_id: int):
        return self.questions.get(question_id)

    async def get_random(self, level: str, category: str, exclude_ids=None):
        for q in self.questions.values():
            if q.level == level and q.category == category and q.id not in (exclude_ids or []):
                return q
        return None

    async def create(self, question):
        if isinstance(question, DTOQuestion):
            q = question
        else:
            # entity -> dto minimal
            q = DTOQuestion(
                id=len(self.questions) + 1,
                title=question.title,
                content=question.content,
                level=question.level,
                category=question.category,
                question_type=question.question_type,
                points=question.points,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                hints=question.hints,
                tags=question.tags,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        if q.id is None:
            q = q.model_copy(update={"id": len(self.questions) + 1})
        self.questions[q.id] = q
        return q


class FakeAnswerRepo(AnswerRepository):
    def __init__(self):
        self.answers: dict[int, DTOAnswer] = {}
        self._next_id = 1

    async def create(self, user_id: int, question_id: int, answer_text: str, answer_type: str, voice_file_id=None):
        ans = DTOAnswer(
            id=self._next_id,
            user_id=user_id,
            question_id=question_id,
            answer_text=answer_text,
            answer_type=answer_type,
            score=None,
            feedback=None,
            voice_file_id=voice_file_id,
            created_at=datetime.utcnow(),
        )
        self.answers[self._next_id] = ans
        self._next_id += 1
        return ans

    async def set_score(self, answer_id: int, score: int, feedback: str):
        ans = self.answers[answer_id]
        updated = ans.model_copy(update={"score": score, "feedback": feedback})
        self.answers[answer_id] = updated
        return updated


class FakeAI(AIProvider):
    async def evaluate(self, question, user_answer: str, answer_type: str = "text", multi_agent_notes=None):
        # simple scoring: full points if keyword in answer
        ok = question.title.split(" ")[0].lower() in user_answer.lower()
        return {"score": question.points if ok else question.points // 2, "feedback": "ok", "is_correct": ok}

    async def transcribe(self, voice_file_path: str) -> str:
        return "transcribed"


class FakeVoice(VoiceStorage):
    async def download_voice(self, file_id: str, bot_token: str, save_path: str) -> bool:
        return True

    async def convert_ogg_to_wav(self, ogg_path: str, wav_path: str) -> bool:
        return True

    async def cleanup(self, *file_paths: str) -> None:
        return None


class FakeOrch(Orchestrator):
    async def prepare_notes(self, category: str, user_id: int, level: str, topic: str) -> str:
        return f"notes for {category}:{topic}"


@pytest.mark.asyncio
async def test_answer_text_flow_updates_score_and_stats():
    users = FakeUserRepo()
    questions = FakeQuestionRepo()
    answers = FakeAnswerRepo()
    ai = FakeAI()
    voice = FakeVoice()
    orch = FakeOrch()

    # seed user and question
    u = await users.create(telegram_id=123, username=None, first_name=None, last_name=None)
    q = await questions.create(
        DTOQuestion(
            id=1,
            title="Индекс в БД",
            content="Что такое индекс?",
            level="middle",
            category="databases",
            question_type="text",
            points=10,
            correct_answer="...",
            explanation=None,
            hints=None,
            tags=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    svc = AnswerAppService(users, questions, answers, ai, voice, orch)

    ans, ev = await svc.answer_text(telegram_id=123, question_id=1, text="индекс это структура")

    assert ev["score"] in (5, 10)
    stats = await users.get_stats(u.id)
    assert stats["questions_answered"] == 1
    assert stats["total_score"] == ev["score"]
