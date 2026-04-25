# Pyronear Analytics Documentation

## Workspace layout

`pyro-analytics` is a uv workspace root. The root `src/analytics` package owns the Typer CLI, shared tooling lives at the root, and domain packages belong under `packages/*`.

## Station package

`packages/station` owns reusable station map publisher library code. It must remain independent from root CLI wiring in `analytics`.

## Station publish CLI

The root CLI delegates station map publishing to the `station` package:

```bash
uv run analytics station publish --source fixture --fixture-path packages/station/tests/fixtures/api-cameras.json --output station-cells.geojson
```

For API-backed S3 publication, configure the environment before running:

```bash
PYRONEAR_API_URL=https://alertapi.pyronear.org \
PYRONEAR_API_TOKEN=... \
STATION_MAP_S3_ENDPOINT_URL=http://localhost:9000 \
STATION_MAP_S3_REGION=us-east-1 \
STATION_MAP_S3_BUCKET=pyronear-public-map-local \
STATION_MAP_S3_ACCESS_KEY_ID=... \
STATION_MAP_S3_SECRET_ACCESS_KEY=... \
uv run analytics station publish --source api
```

The command prints only summary counts and artifact metadata. It must not print credentials, exact source coordinates, or raw API records.

For the full manual workflow, environment variables, MinIO notes, object key policy, and privacy review checklist, see [Station Publisher Runbook](station-publisher-runbook.md).

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
uv run pytest
```
