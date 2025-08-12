run-api:
	uv run python main.py --mode api

run-bot:
	uv run python main.py --mode bot

seed:
	uv run python scripts/seed_questions.py questions.example.yaml

test:
	uv run pytest -q

test-cov:
	uv run pytest --cov=src -q

lint:
	uv run ruff check .

mypy:
	uv run mypy src
