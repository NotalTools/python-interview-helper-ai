from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class ReviewerAgent(BaseAgent):
    name = "reviewer"
    description = "Дает ревью по стилю, качеству и устойчивости"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        hints = (
            "Проверь: типы, обработку исключений, повторное использование кода, логирование, тестируемость, PEP8."
        )
        return AgentMessage(role=self.name, content=f"Ревью чек-лист: {hints}")
