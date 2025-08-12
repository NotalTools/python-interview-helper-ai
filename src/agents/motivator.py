from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class MotivatorAgent(BaseAgent):
    name = "motivator"
    description = "Поддерживает и предлагает следующие шаги"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        return AgentMessage(
            role=self.name,
            content="Отлично! Продолжай в том же духе. Готов предложить мини-челлендж или новую тему."
        )
