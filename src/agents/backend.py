from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class APIDesignerAgent(BaseAgent):
    name = "be_api"
    description = "Контракты API, версии, ошибки, идемпотентность"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Определи контракты, коды ошибок, идемпотентные ключи, версионирование и совместимость."
        )
        return AgentMessage(role=self.name, content=content)

class PerfProfilerAgent(BaseAgent):
    name = "be_perf"
    description = "Профилирование производительности"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Найди горячие пути, кешируй, снижай аллокации, оптимизируй обращения к БД/сети."
        )
        return AgentMessage(role=self.name, content=content)

class ReliabilityEngineerAgent(BaseAgent):
    name = "be_reliability"
    description = "Надежность: ретраи/дедлайны/лимиты"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Задай дедлайны, ретраи с джиттером, лимитируй запросы, проработай идемпотентность."
        )
        return AgentMessage(role=self.name, content=content)

class ObservabilityAgent(BaseAgent):
    name = "be_obs"
    description = "Обсервабилити: метрики/трейсы/логи"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Добавь метрики (RPS, p95), распределённые трейсинги, корреляцию логов и контекст запросов."
        )
        return AgentMessage(role=self.name, content=content)
