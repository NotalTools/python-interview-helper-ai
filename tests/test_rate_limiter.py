from __future__ import annotations
from src.rate_limit import DailyUserLimiter


def test_daily_user_limiter_blocks_after_limit():
    limiter = DailyUserLimiter(limit=2)
    user_id = 42
    assert limiter.allow(user_id) is True
    assert limiter.allow(user_id) is True
    assert limiter.allow(user_id) is False
