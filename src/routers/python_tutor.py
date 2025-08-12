from __future__ import annotations
from fastapi import APIRouter, HTTPException
import uuid

from ..agents.base import AgentContext
from ..orchestrator import PythonMentorOrchestrator
from ..schemas import SessionCreate, SessionState, UserCode
from ..container import get_tutor_app_service

router = APIRouter(prefix="/python", tags=["python-mentor"])

# In-memory сессии (для архитектуры)
SESSIONS: dict[str, AgentContext] = {}


@router.post("/sessions", response_model=SessionState)
async def create_session(payload: SessionCreate):
    session_id = str(uuid.uuid4())
    ctx = AgentContext(user_id=payload.user_id, level=payload.level, topic=payload.topic)
    SESSIONS[session_id] = ctx

    orch = PythonMentorOrchestrator()
    responses = await orch.run_round(ctx)

    return SessionState(
        session_id=session_id,
        user_id=payload.user_id,
        level=payload.level,
        topic=payload.topic,
        history=[r.model_dump() for r in responses],
    )


@router.post("/sessions/{session_id}/run")
async def run_code(session_id: str, body: UserCode):
    if session_id not in SESSIONS:
        raise HTTPException(404, "session not found")
    tutor = get_tutor_app_service()
    result = await tutor.run_code(body.code, body.stdin or "")
    return result
