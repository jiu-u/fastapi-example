.PHONY: dev
dev:
	uvicorn main:app --reload --port 8000

.PHONY: check
check:
	uv run ruff check

.PHONY: format
format:
	uv run ruff format

.PHONY: fix
fix:
	uv run ruff check --fix


