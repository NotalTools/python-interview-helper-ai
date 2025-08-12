from __future__ import annotations
from typing import Optional, Dict, Any

from ..services import get_ai_service
from ..models import Question
from ..domain.ports import AIProvider


class DefaultAIProvider(AIProvider):
    def __init__(self) -> None:
        self._svc = get_ai_service()

    async def evaluate(self, question: Question, user_answer: str, answer_type: str = "text", multi_agent_notes: Optional[str] = None) -> Dict[str, Any]:
        evaluation = await self._svc.evaluate_answer(question, user_answer, answer_type, multi_agent_notes)
        return {
            "score": evaluation.score,
            "feedback": evaluation.feedback,
            "is_correct": evaluation.is_correct,
        }

    async def transcribe(self, voice_file_path: str) -> str:
        return await self._svc.transcribe_voice(voice_file_path)
