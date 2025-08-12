#!/usr/bin/env python3
from __future__ import annotations
import asyncio
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.container import get_question_app_service
from src.domain.entities import QuestionEntity
from src.database import database


async def main(yaml_path: str):
    await database.connect()
    await database.create_tables()

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    qs = get_question_app_service()

    count = 0
    for item in data:
        q = QuestionEntity(
            id=0,
            title=item["title"],
            content=item["content"],
            level=item["level"],
            category=item["category"],
            question_type=item.get("question_type", "text"),
            points=int(item.get("points", 10)),
            correct_answer=item["correct_answer"],
            explanation=item.get("explanation"),
            hints=item.get("hints"),
            tags=item.get("tags"),
        )
        q.validate()
        await qs.create(q)
        count += 1

    print(f"Imported {count} questions from {yaml_path}")
    await database.disconnect()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scripts/seed_questions.py path/to/questions.yaml")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
