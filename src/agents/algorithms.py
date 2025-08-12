from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class TaskmasterAgent(BaseAgent):
    name = "alg_taskmaster"
    description = "Формализует задачу и ограничения"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Сформулируй вход/выход, ограничения по памяти/времени, и что считается корректным решением."
        )
        return AgentMessage(role=self.name, content=content)

class ComplexityAgent(BaseAgent):
    name = "alg_complexity"
    description = "Оценивает асимптотику и выбор структур данных"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Оцени временную/пространственную сложность, обоснуй выбор структур данных (массив/хеш/дерево/куча)."
        )
        return AgentMessage(role=self.name, content=content)

class TestGenAgent(BaseAgent):
    name = "alg_testgen"
    description = "Генерирует тесты: edge, большие, случайные"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Сгенерируй граничные кейсы, большие входы, и случайные тесты; проверь повторяемость и покрытие."
        )
        return AgentMessage(role=self.name, content=content)

class AlgOptimizerAgent(BaseAgent):
    name = "alg_optimizer"
    description = "Предлагает оптимизации и упрощения"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        content = (
            "Подскажи более эффективный подход, удаление лишних проходов, предвычисление, кэширование."
        )
        return AgentMessage(role=self.name, content=content)
