from __future__ import annotations
from typing import List

from .agents.base import AgentContext, AgentMessage
from .agents.teacher import TeacherAgent
from .agents.explainer import ExplainerAgent
from .agents.coach import CoachAgent
from .agents.reviewer import ReviewerAgent
from .agents.motivator import MotivatorAgent


class PythonMentorOrchestrator:
    """Простой раунд-робин оркестратор для демонстрации архитектуры"""

    def __init__(self) -> None:
        self.agents = [
            TeacherAgent(),
            ExplainerAgent(),
            CoachAgent(),
            ReviewerAgent(),
            MotivatorAgent(),
        ]

    async def run_round(self, ctx: AgentContext) -> List[AgentMessage]:
        responses: List[AgentMessage] = []
        for agent in self.agents:
            msg = await agent.act(ctx)
            ctx.history.append(msg)
            responses.append(msg)
        return responses
