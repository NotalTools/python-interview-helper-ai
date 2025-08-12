from __future__ import annotations
from typing import Optional
from .base import BaseAgent, AgentContext, AgentMessage

class CoachAgent(BaseAgent):
    name = "coach"
    description = "Выдает задачу и критерии проверки"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        task = (
            "Напиши функцию get_user_repos(username: str) -> list, которая вернет список имен репозиториев "
            "пользователя GitHub. Используй requests, обработай ошибки, таймаут 10 секунд."
        )
        tests = (
            "- пустая строка -> ValueError;\n"
            "- несуществующий пользователь -> вернуть пустой список;\n"
            "- существующий пользователь -> вернуть список строк."
        )
        return AgentMessage(role=self.name, content=f"Задача:\n{task}\n\nКритерии:\n{tests}")
