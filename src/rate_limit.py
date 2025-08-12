from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, Tuple

from .config import settings


class DailyUserLimiter:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._store: Dict[int, Tuple[int, datetime]] = {}

    def allow(self, user_id: int) -> bool:
        now = datetime.utcnow()
        count, reset_at = self._store.get(user_id, (0, now + timedelta(days=1)))
        if now >= reset_at:
            count = 0
            reset_at = now + timedelta(days=1)
        if count >= self.limit:
            self._store[user_id] = (count, reset_at)
            return False
        self._store[user_id] = (count + 1, reset_at)
        return True


limiter = DailyUserLimiter(settings.daily_limit_per_user)
