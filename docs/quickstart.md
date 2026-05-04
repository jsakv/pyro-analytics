# Quickstart

Use this path to verify the workspace and generate a local Pyromap artifact
without live backend or S3 credentials.

## Prerequisites

- Python 3.12 or 3.13
- `uv`

## Install The Workspace

```bash
make setup
```

This installs the locked workspace and the local pre-commit Git hooks.

## Inspect The CLI

```bash
uv run pyro-analytics --help
```

## Run The Test Suite

```bash
uv run pytest
```

## Publish A Fixture Artifact

```bash
uv run pyro-analytics pyromap publish --source fixture --fixture-path packages/pyromap/tests/fixtures/api-cameras.json --output camera-cells.geojson
```

The command writes `camera-cells.geojson`, a public GeoJSON artifact that groups
cameras into deterministic H3 cells.

## Build The Documentation

```bash
make build-docs
```

The command regenerates the package reference before writing the built site to
`docs/_build/html`.

## Where To Go Next

- [Sources](sources.md) explains the reusable dlt source package boundary.
- [Pyronear API](pyronear-api.md) documents the implemented backend source contract.
- [Pyromap](pyromap.md) explains the current camera map workflow.
- [Contracts](pyromap-contracts.md) define stable behavior for map consumers.
- [Runbooks](pyromap-runbooks.md) contain operational publishing steps.
