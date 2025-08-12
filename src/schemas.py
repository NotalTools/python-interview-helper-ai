from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class SessionCreate(BaseModel):
    user_id: int
    level: str
    topic: str

class SessionState(BaseModel):
    session_id: str
    user_id: int
    level: str
    topic: str
    history: List[dict] = Field(default_factory=list)

class UserCode(BaseModel):
    code: str
    stdin: Optional[str] = ""

class ExecutionResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    output: str = ""
    ran: bool = True
