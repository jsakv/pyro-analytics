# Pyronear Analytics Workspace

Pyronear Analytics is a uv workspace for wildfire data analysis and operational insight packages.

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
uv run pytest --cov=packages
```

## Package layout

- `packages/`: workspace packages, added as `packages/*`
- `tests/`: root workspace configuration tests
- `pyproject.toml`: lint/type/test/coverage configuration

The root project is not an installable package. Domain implementation belongs in workspace members under `packages/*`.

## Lint and type policy

This scaffold preserves strict defaults aligned with the `pyproject 2` ruleset intent:
- Ruff lint profile remains strict with `target-version = "py39"` for conservative compatibility.
- Mypy strict settings are enabled by default.
- Coverage is configured with branch tracking and workspace package source filtering.

If you relax any strictness defaults, document the rationale in this README to keep team expectations explicit.
