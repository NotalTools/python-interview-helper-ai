from __future__ import annotations
from typing import Optional

from ..domain.ports import DocsProvider


class Context7DocsProvider(DocsProvider):
    def __init__(self) -> None:
        self.client = None  # удалено по требованию; провайдер будет неактивен

    async def get_docs(self, library_id: str, topic: Optional[str] = None, tokens: int = 2000) -> str:
        # Интеграция с Context7 отключена. Возвращаем пустую строку.
        return ""
