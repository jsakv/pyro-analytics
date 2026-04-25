# Pyronear Analytics Documentation

## Workspace layout

`pyro-analytics` is a uv workspace root. The root `src/analytics` package owns the Typer CLI, shared tooling lives at the root, and domain packages belong under `packages/*`.

## Station package

`packages/station` owns reusable station map publisher library code. It must remain independent from root CLI wiring in `analytics`.

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
