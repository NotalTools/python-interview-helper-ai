from __future__ import annotations
from .base import BaseAgent, AgentContext, AgentMessage

class ExplainerAgent(BaseAgent):
    name = "explainer"
    description = "Дает простой рабочий пример и объясняет построчно"

    async def act(self, ctx: AgentContext) -> AgentMessage:
        example = (
            "import requests\n"
            "resp = requests.get('https://api.github.com/users/octocat/repos', timeout=10)\n"
            "resp.raise_for_status()\n"
            "data = resp.json()\n"
            "print(len(data))\n"
        )
        explanation = (
            "- импортируем requests;\n"
            "- делаем GET;\n"
            "- проверяем статус;\n"
            "- парсим JSON;\n"
            "- печатаем количество репозиториев."
        )
        return AgentMessage(role=self.name, content=f"Пример:\n```python\n{example}```\nРазбор:\n{explanation}")
