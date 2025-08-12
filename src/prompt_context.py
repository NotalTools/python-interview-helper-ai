from __future__ import annotations
from typing import Optional

from .domain.rubrics import build_rubric_text


def build_prompt_context(category: str, notes: Optional[str]) -> str:
    parts: list[str] = []
    if notes:
        parts.append("Мнения экспертов по теме (конспект):\n" + notes)
    rubric = build_rubric_text(category)
    if rubric:
        parts.append(rubric)
    return "\n\n".join(parts) if parts else ""
