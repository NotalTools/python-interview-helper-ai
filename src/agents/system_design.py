from __future__ import annotations
from typing import Dict
from .base import BaseAgent, AgentContext, AgentMessage

class ArchitectAgent(BaseAgent):
    name = "architect"
    description = "High-level архитектура: компоненты, API, данные"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Компоненты: Gateway/API → Services → DB/Cache → Async workers. "
            "Определи контракты API, границы сервисов, и модель данных на верхнем уровне."
        )
        return AgentMessage(role=self.name, content=content)

class StorageAgent(BaseAgent):
    name = "storage"
    description = "Хранилища: выбор БД, индексы, шардинг/репликация"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Выбор БД: OLTP (PostgreSQL) + аналитика (ClickHouse). Индексы по ключам доступа, "
            "реплика для чтения, шардинг по user_id/region при росте."
        )
        return AgentMessage(role=self.name, content=content)

class ReliabilityAgent(BaseAgent):
    name = "reliability"
    description = "Надежность/SRE: деградация, ретраи, лимиты, SLI/SLO"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Circuit breaker, тайм-ауты, ретраи с джиттером, rate limiting, "
            "коды ошибок и идемпотентность. Метрики: латентность, ошибки, доля удачных."
        )
        return AgentMessage(role=self.name, content=content)

class TradeoffsAgent(BaseAgent):
    name = "tradeoffs"
    description = "Анализ компромиссов по альтернативам"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Trade-offs: простота vs масштабируемость; консистентность vs доступность; "
            "горизонтальное масштабирование vs сложность управления."
        )
        return AgentMessage(role=self.name, content=content)
