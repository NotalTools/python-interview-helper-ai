from __future__ import annotations
from typing import List

from .agents.base import AgentContext, AgentMessage
from .agents.system_design import ArchitectAgent, StorageAgent, ReliabilityAgent, TradeoffsAgent
from .config import AppConstants


AGENT_REGISTRY = {
    "architect": ArchitectAgent,
    "storage": StorageAgent,
    "reliability": ReliabilityAgent,
    "tradeoffs": TradeoffsAgent,
}


class InterviewOrchestrator:
    """Мультиагентный конвейер для интервью по категориям. MVP: system_design."""

    def __init__(self, category: str):
        self.category = category
        names = AppConstants.INTERVIEW_CATEGORY_PIPELINES.get(category, [])
        self.agents = [AGENT_REGISTRY[name]() for name in names if name in AGENT_REGISTRY]

    async def critique(self, ctx: AgentContext) -> List[AgentMessage]:
        outputs: List[AgentMessage] = []
        for agent in self.agents:
            msg = await agent.act(ctx)
            ctx.history.append(msg)
            outputs.append(msg)
        return outputs
