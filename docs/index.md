# Pyronear Analytics Documentation

## Workspace layout

`pyro-analytics` is a uv workspace root. The root `src/analytics` package owns the Typer CLI, shared tooling lives at the root, and domain packages belong under `packages/*`.

## Camera package

`packages/cameras` owns reusable camera map publisher library code. It must remain independent from root CLI wiring in `analytics`.

## Camera publish CLI

The root CLI delegates camera map publishing to the `cameras` package:

```bash
uv run analytics cameras publish --source fixture --fixture-path packages/cameras/tests/fixtures/api-cameras.json --output camera-cells.geojson
```

For API-backed S3 publication, configure the environment before running:

```bash
PYRONEAR_API_URL=https://alertapi.pyronear.org \
PYRONEAR_API_TOKEN=... \
CAMERA_MAP_S3_ENDPOINT_URL=http://localhost:9000 \
CAMERA_MAP_S3_REGION=us-east-1 \
CAMERA_MAP_S3_BUCKET=pyronear-public-map-local \
CAMERA_MAP_S3_ACCESS_KEY_ID=... \
CAMERA_MAP_S3_SECRET_ACCESS_KEY=... \
uv run analytics cameras publish --source api
```

The command prints only summary counts and artifact metadata. It must not print credentials, exact source coordinates, or raw API records.

For the full manual workflow, environment variables, MinIO notes, object key policy, and privacy review checklist, see [Camera Publisher Runbook](camera-publisher-runbook.md).

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
