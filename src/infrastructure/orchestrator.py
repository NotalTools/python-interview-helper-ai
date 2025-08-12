from __future__ import annotations
from ..domain.ports import Orchestrator
from ..interview_service import InterviewService


class DefaultOrchestrator(Orchestrator):
    async def prepare_notes(self, category: str, user_id: int, level: str, topic: str) -> str:
        return await InterviewService.prepare_expert_notes(category, user_id, level, topic)
