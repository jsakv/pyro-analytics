.PHONY: sync format lint type test test-cov check

sync:
	uv sync

format:
	uv run ruff format .

lint:
	uv run ruff check .

type:
	uv run mypy

test:
	uv run pytest

test-cov:
	uv run pytest --cov=analytics --cov=packages

check:
	uv run ruff format . --check
	uv run ruff check .
	uv run mypy
	uv run pytest
