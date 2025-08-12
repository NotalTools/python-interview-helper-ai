from __future__ import annotations
from typing import Optional
import aiohttp

from ...src.config import settings


class Context7Client:
    def __init__(self) -> None:
        base = settings.context7_api_base.strip()
        token = settings.context7_api_token.strip()
        self.base_url = base or ""
        self.token = token or ""
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_docs(self, library_id: str, topic: Optional[str] = None, tokens: int = 2000) -> str:
        if not self.base_url or not self.token:
            return ""
        session = await self._ensure_session()
        url = f"{self.base_url}/docs"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {"library_id": library_id, "topic": topic, "tokens": tokens}
        try:
            async with session.post(url, json=payload, headers=headers, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("content", "")
                return ""
        except Exception:
            return ""
