from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class ThreatModelerAgent(BaseAgent):
    name = "sec_threats"
    description = "Моделирование угроз: STRIDE, DFD"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Определи границы доверия, поверхность атаки, угрозы STRIDE и меры снижения."
        )
        return AgentMessage(role=self.name, content=content)

class SecureCoderAgent(BaseAgent):
    name = "sec_secure_code"
    description = "Риски в коде: инъекции, XSS/CSRF, SSRF"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Проверь ввод/валидацию, параметризованные запросы, политики CORS, безопасные сериализации."
        )
        return AgentMessage(role=self.name, content=content)

class CryptoReviewerAgent(BaseAgent):
    name = "sec_crypto"
    description = "Криптография и секреты"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Выбор алгоритмов, режимов, хранение/ротация ключей, PFS, TLS конфигурация."
        )
        return AgentMessage(role=self.name, content=content)

class ComplianceAgent(BaseAgent):
    name = "sec_compliance"
    description = "PII/аудит/ретеншн"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Категоризуй данные, доступ, аудит, сроки хранения/удаления в соответствии с политиками."
        )
        return AgentMessage(role=self.name, content=content)
