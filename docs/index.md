# Pyronear Analytics Documentation

## Workspace layout

`pyro-analytics` is a uv workspace root. Shared tooling lives at the root, and domain packages belong under `packages/*`.

## Local docs workflow

```bash
uv sync
uv run pytest
```

## Development checks

```bash
uv run ruff format . --check
uv run ruff check .
uv run mypy
```
