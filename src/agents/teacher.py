from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class TeacherAgent(BaseAgent):
    name = "teacher"
    description = "Планирует обучение и дает теорию"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        plan = "- Введение в тему\n- Ключевые концепции\n- Частые ошибки\n- Мини-задача"
        content = (
            f"Уровень: {ctx.level}. Тема: {ctx.topic}.\n"
            f"План занятия:\n{plan}\n\n"
            f"Теория: кратко объясню ключевые идеи и что важно запомнить."
        )
        return AgentMessage(role=self.name, content=content)
