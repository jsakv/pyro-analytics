# Pyronear Analytics

Pyronear Analytics provides Python tools for wildfire data analysis and operational insight.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

## Tooling defaults

- Dependency and environment management: `uv`
- Lint and format: `ruff`
- Tests: `pytest`
- Local gate runner: `pre-commit`
- Type checks: `mypy`

## Quick start

```bash
uv sync
uv run pytest
```

## Development workflow

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest --cov=analytics
```

## Package layout

- `src/analytics/`: library source
- `tests/conftest.py`: shared pytest configuration
- `tests/analytics/`: test suite mirroring source package boundaries
- `pyproject.toml`: lint/type/test/coverage configuration

## Lint and type policy

This scaffold preserves strict defaults aligned with the `pyproject 2` ruleset intent:
- Ruff lint profile remains strict with `target-version = "py39"` for conservative compatibility.
- Mypy strict settings are enabled by default.
- Coverage is configured with branch tracking and package source filtering.

If you relax any strictness defaults, document the rationale in this README to keep team expectations explicit.
