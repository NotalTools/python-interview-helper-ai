from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    role: str = Field(..., description="Имя агента-отправителя")
    content: str = Field(..., description="Текст сообщения")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Метаданные сообщения")


class AgentContext(BaseModel):
    user_id: int
    level: str
    topic: str
    history: List[AgentMessage] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    code_under_review: Optional[str] = None


class BaseAgent:
    name: str = "agent"
    description: str = ""

    async def act(self, ctx: AgentContext) -> AgentMessage:
        raise NotImplementedError
