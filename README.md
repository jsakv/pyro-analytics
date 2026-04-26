# Pyronear Analytics Workspace

Pyronear Analytics is a uv workspace for wildfire data analysis and operational insight packages. The root `analytics` package owns the repository CLI, while domain libraries live under `packages/*`.

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

## Camera publisher

The root CLI exposes camera map publication while domain logic stays in `packages/cameras`:

```bash
uv run analytics cameras publish --source fixture --fixture-path packages/cameras/tests/fixtures/api-cameras.json --output camera-cells.geojson
```

For a larger map demo, use `examples/cameras/demo-api-cameras.json` or the generated `examples/cameras/demo-camera-cells.geojson`. The demo source contains 66 synthetic camera records across fire-prone forest regions in France, Spain, and Germany, with dense cells containing 2, 3, and 4 cameras.

Singleton camera cells are published as deterministic neighboring H3 cells by default, with `CAMERA_MAP_SINGLETON_CELL_SHIFT_SALT` available for production salt configuration.

For API-backed publishing, S3-compatible settings, MinIO notes, object key policy, and the manual runbook, see [docs/camera-publisher-runbook.md](docs/camera-publisher-runbook.md).

## Development workflow

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest --cov=analytics --cov=packages
uv run analytics --help
```

## Package layout

- `src/analytics/`: repository CLI package and Typer app entrypoint
- `packages/`: workspace packages, added as `packages/*`
- `packages/cameras/`: reusable camera map publisher library
- `tests/`: root CLI and workspace configuration tests
- `pyproject.toml`: lint/type/test/coverage configuration

The root `analytics` package is command wiring only. Domain implementation belongs in workspace members under `packages/*`.

## Lint and type policy

This scaffold preserves strict defaults aligned with the `pyproject 2` ruleset intent:
- Ruff lint profile remains strict with `target-version = "py39"` for conservative compatibility.
- Mypy strict settings are enabled by default.
- Coverage is configured with branch tracking for the root CLI package and workspace package source filtering.

If you relax any strictness defaults, document the rationale in this README to keep team expectations explicit.
