from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class RubricItem:
    name: str
    description: str
    weight: int  # суммарный вес по критериям должен быть равен 100


@dataclass(frozen=True)
class Rubric:
    category: str
    items: List[RubricItem]

    def total_weight(self) -> int:
        return sum(i.weight for i in self.items)

    def as_text(self) -> str:
        lines = ["Рубрика оценки (сумма весов = 100):"]
        for i in self.items:
            lines.append(f"- {i.name} ({i.weight}%): {i.description}")
        return "\n".join(lines)


DEFAULT_RUBRICS: Dict[str, Rubric] = {
    "system_design": Rubric(
        category="system_design",
        items=[
            RubricItem("Архитектура", "ясность, целостность компонентов и API", 35),
            RubricItem("Масштабируемость/Надёжность", "SLO, деградация, кэширование, репликация", 35),
            RubricItem("Trade-offs", "сравнение альтернатив и явные компромиссы", 20),
            RubricItem("Безопасность", "аутентификация/авторизация, управление секретами", 10),
        ],
    ),
    "algorithms": Rubric(
        category="algorithms",
        items=[
            RubricItem("Корректность", "соответствие условию, обработка edge-кейсов", 40),
            RubricItem("Сложность", "адекватная асимптотика и выбор структур", 35),
            RubricItem("Пояснение", "чёткое объяснение подхода", 25),
        ],
    ),
    "databases": Rubric(
        category="databases",
        items=[
            RubricItem("Модель данных", "ключи, индексы, нормализация/денормализация", 35),
            RubricItem("Запросы и планы", "оптимизация запросов, индексация", 35),
            RubricItem("Транзакции/Репликация", "изол., конфликты, реплика/шардинг", 30),
        ],
    ),
    "networking": Rubric(
        category="networking",
        items=[
            RubricItem("Протокол/Транспорт", "выбор и настройки", 30),
            RubricItem("Латентность", "тюнинг, пулы, пайплайнинг", 35),
            RubricItem("Надёжность", "LB, health-checks, деградация", 35),
        ],
    ),
    "security": Rubric(
        category="security",
        items=[
            RubricItem("Моделирование угроз", "границы доверия, STRIDE", 35),
            RubricItem("Безопасный код", "инъекции, XSS/CSRF, SSRF", 35),
            RubricItem("Крипто/PII", "алгоритмы, ключи, комплаенс", 30),
        ],
    ),
    "backend": Rubric(
        category="backend",
        items=[
            RubricItem("API дизайн", "контракты, версии, ошибки", 30),
            RubricItem("Производительность", "горячие пути, кэширование", 35),
            RubricItem("Надёжность/Обсервабилити", "ретраи, лимиты, метрики/трейсы", 35),
        ],
    ),
}


def build_rubric_text(category: str) -> str:
    rubric = DEFAULT_RUBRICS.get(category)
    if not rubric:
        return ""
    if rubric.total_weight() != 100:
        # на всякий случай нормализуем указанием суммы
        return rubric.as_text() + f"\n(Внимание: текущая сумма весов = {rubric.total_weight()})"
    return rubric.as_text()
