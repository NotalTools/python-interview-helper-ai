from __future__ import annotations
import pytest
from datetime import datetime

from src.application.user_services import QuestionAppService
from src.domain.ports import UserRepository, QuestionRepository
from src.models import Question as DTOQuestion


class FakeUserRepo(UserRepository):
    async def get_by_telegram_id(self, telegram_id: int):
        return None
    async def create(self, *a, **kw):
        raise NotImplementedError
    async def update_by_telegram_id(self, *a, **kw):
        raise NotImplementedError
    async def get_stats(self, *a, **kw):
        return {}


class FakeQuestionRepo(QuestionRepository):
    def __init__(self):
        self.data = [
            DTOQuestion(id=1, title="A", content="db", level="middle", category="databases", question_type="text", points=10, correct_answer="", explanation=None, hints=None, tags=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            DTOQuestion(id=2, title="B", content="net", level="senior", category="networking", question_type="text", points=10, correct_answer="", explanation=None, hints=None, tags=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            DTOQuestion(id=3, title="C", content="db2", level="middle", category="databases", question_type="text", points=10, correct_answer="", explanation=None, hints=None, tags=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        ]
    async def get_by_id(self, question_id: int):
        return next((x for x in self.data if x.id == question_id), None)
    async def get_random(self, *a, **kw):
        return self.data[0]
    async def create(self, question):
        self.data.append(question)
        return question
    async def search(self, level=None, category=None, q=None, limit=20, offset=0):
        items = [x for x in self.data if (not level or x.level==level) and (not category or x.category==category)]
        return items[offset:offset+limit]
    async def update(self, *a, **kw):
        return None
    async def delete(self, *a, **kw):
        return True
    async def count(self, level=None, category=None, q=None):
        return len([x for x in self.data if (not level or x.level==level) and (not category or x.category==category)])


@pytest.mark.asyncio
async def test_search_returns_items_and_total():
    qs = QuestionAppService(FakeUserRepo(), FakeQuestionRepo())
    res = await qs.search(level="middle", category="databases", q=None, limit=10, offset=0)
    assert "items" in res and "total" in res
    assert res["total"] == 2
    assert len(res["items"]) == 2
