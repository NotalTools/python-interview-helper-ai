from __future__ import annotations
from typing import List, Tuple, Dict
from time import time

from .interview_orchestrator import InterviewOrchestrator
from .agents.base import AgentContext, AgentMessage


_CACHE: Dict[Tuple[str, str, str], Tuple[float, str]] = {}
_TTL = 600.0  # 10 минут


async def build_multi_agent_notes(messages: List[AgentMessage]) -> str:
    parts = [f"- {m.role}: {m.content}" for m in messages]
    return "\n".join(parts)


class InterviewService:
    """Интервью-сервис: собирает мультиагентные заметки для выбранных категорий"""

    @staticmethod
    async def prepare_expert_notes(category: str, user_id: int, level: str, topic: str) -> str:
        key = (category, level, topic)
        now = time()
        cached = _CACHE.get(key)
        if cached and (now - cached[0] < _TTL):
            return cached[1]

        orch = InterviewOrchestrator(category)
        if not orch.agents:
            return ""
        ctx = AgentContext(user_id=user_id, level=level, topic=topic)
        outputs = await orch.critique(ctx)
        notes = await build_multi_agent_notes(outputs)
        _CACHE[key] = (now, notes)
        return notes
