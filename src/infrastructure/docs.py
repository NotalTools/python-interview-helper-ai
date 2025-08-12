from __future__ import annotations
from typing import Optional

from .mcp.context7_client import Context7Client  # предполагаемый клиент, заглушка
from ..domain.ports import DocsProvider


class Context7DocsProvider(DocsProvider):
    def __init__(self) -> None:
        self.client = Context7Client()

    async def get_docs(self, library_id: str, topic: Optional[str] = None, tokens: int = 2000) -> str:
        # Заглушка: в реальном проекте использовать SDK/HTTP клиента Context7
        try:
            return await self.client.get_docs(library_id=library_id, topic=topic, tokens=tokens)
        except Exception:
            return ""
