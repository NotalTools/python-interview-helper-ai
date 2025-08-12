from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class ProtocolAnalystAgent(BaseAgent):
    name = "net_protocols"
    description = "Протоколы и транспорт: HTTP/2/3, gRPC, TLS"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Выбор протокола и настроек TLS, пайплайнинг/мультиплексирование, компрессия заголовков."
        )
        return AgentMessage(role=self.name, content=content)

class LatencyOptimizerAgent(BaseAgent):
    name = "net_latency"
    description = "Оптимизация латентности и TCP-тюнинг"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Определи горячие RTT, тюнинг буферов, keep-alive, коннект‑пулы, сокращение чатов."
        )
        return AgentMessage(role=self.name, content=content)

class LoadBalancerAgent(BaseAgent):
    name = "net_lb"
    description = "Балансировка, health‑checks, sticky"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Схема LB: RR/LC, health‑checks, outlier detection, sticky/идемпотентность под ретраи."
        )
        return AgentMessage(role=self.name, content=content)

class ChaosAgent(BaseAgent):
    name = "net_chaos"
    description = "Сценарии сбоев: packet loss/jitter, деградация"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Смоделируй потери пакетов/джиттер, проверь тайм-ауты/ретраи, graceful деградацию."
        )
        return AgentMessage(role=self.name, content=content)
