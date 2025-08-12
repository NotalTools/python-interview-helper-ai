from __future__ import annotations
from typing import List

from .interview_orchestrator import InterviewOrchestrator
from .agents.base import AgentContext, AgentMessage


async def build_multi_agent_notes(messages: List[AgentMessage]) -> str:
    parts = [f"- {m.role}: {m.content}" for m in messages]
    return "\n".join(parts)


class InterviewService:
    """Интервью-сервис: собирает мультиагентные заметки для выбранных категорий"""

    @staticmethod
    async def prepare_expert_notes(category: str, user_id: int, level: str, topic: str) -> str:
        orch = InterviewOrchestrator(category)
        if not orch.agents:
            return ""
        ctx = AgentContext(user_id=user_id, level=level, topic=topic)
        outputs = await orch.critique(ctx)
        return await build_multi_agent_notes(outputs)
