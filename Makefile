run-api:
	uv run uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

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

docker-up:
	docker compose up -d --build

docker-logs:
	docker compose logs -f api

docker-down:
	docker compose down -v
