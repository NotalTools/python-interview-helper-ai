from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class DBModelerAgent(BaseAgent):
    name = "db_modeler"
    description = "Моделирование данных: нормализация/денормализация"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Определи сущности и связи, ключи, индексы; баланс нормализации и денормализации для чтения/записи."
        )
        return AgentMessage(role=self.name, content=content)

class QueryOptimizerAgent(BaseAgent):
    name = "db_query_optimizer"
    description = "Оптимизация запросов и индексов"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Проверь планы выполнения, добавь составные индексы, перепиши запросы для снижения полного скана."
        )
        return AgentMessage(role=self.name, content=content)

class ConsistencyAgent(BaseAgent):
    name = "db_consistency"
    description = "Транзакции/изоляция/блокировки"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Укажи уровни изоляции, где возможны фантомы/грязное чтение; обработай deadlocks и ретраи."
        )
        return AgentMessage(role=self.name, content=content)

class ReplicationAgent(BaseAgent):
    name = "db_replication"
    description = "Репликация/шардирование/миграции"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Реплика чтения, шардирование по ключу доступа, план миграций с backfill и откатами."
        )
        return AgentMessage(role=self.name, content=content)
