from __future__ import annotations
from typing import Optional, Dict, Any
import httpx

PISTON_URL = "https://emkc.org/api/v2/piston/execute"


async def execute_python(code: str, stdin: str = "") -> Dict[str, Any]:
    payload = {
        "language": "python",
        "version": "3.10.0",
        "files": [{"name": "main.py", "content": code}],
        "stdin": stdin,
        "args": [],
        "compile_timeout": 10000,
        "run_timeout": 10000,
        "compile_memory_limit": -1,
        "run_memory_limit": -1,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(PISTON_URL, json=payload)
        resp.raise_for_status()
        return resp.json()
