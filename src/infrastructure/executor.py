from __future__ import annotations
from typing import Dict, Any

from ..code_executor import execute_python
from ..domain.ports import CodeExecutor


class PistonExecutor(CodeExecutor):
    async def execute(self, code: str, stdin: str = "") -> Dict[str, Any]:
        return await execute_python(code, stdin)
