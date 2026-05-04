<p align="center">
    <img src="https://raw.githubusercontent.com/pyronear/pyro-engine/develop/docs/source/_static/img/pyronear-logo-dark.png" alt="Pyronear logo" width="320">
</p>

<h1 align="center">Analytics</h1>

<p align="center">
    <a href="https://github.com/jsakv/pyro-analytics/actions/workflows/main.yml">
        <img src="https://github.com/jsakv/pyro-analytics/actions/workflows/main.yml/badge.svg" alt="CI" /></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.13-blue" alt="Python 3.12 | 3.13" />
    <img src="https://img.shields.io/badge/package%20manager-uv-654ff0" alt="Package manager: uv" />
    <img src="https://img.shields.io/badge/code%20style-ruff-d7ff64" alt="Code style: Ruff" />
</p>

Pyronear Analytics helps analyze data produced by deployed stations and backend systems, from embedded-computer telemetry to platform usage signals. The `analytics` package provides the `pyro-analytics` CLI, and each domain package under `packages/*` can focus on one analysis area.

<!-- TOC -->

- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Camera publisher](#camera-publisher)
- [Examples](#examples)
  - [Camera demo data](#camera-demo-data)
- [Documentation](#documentation)
- [Contributing](#contributing)
  - [Workspace layout](#workspace-layout)
  - [Quality checks](#quality-checks)
  - [Continuous integration](#continuous-integration)
- [Credits](#credits)

<!-- /TOC -->

## Getting started

### Prerequisites

- Python 3.12 or 3.13
- [uv](https://docs.astral.sh/uv/)

This workspace uses:

- Dependency and environment management: `uv`
- Lint and format: `ruff`
- Tests: `pytest`
- Type checks: `mypy`
- Local checks: `pre-commit`

### Installation

Clone the repository, install the locked workspace, and run the tests:

```bash
uv sync
uv run pytest
```

## Usage

The workspace is organized around small operational analytics flows that can be
run from the root `pyro-analytics` CLI. Today, the main shipped flow publishes camera
coverage data for map consumers; future packages can follow the same pattern for
station telemetry, backend health signals, and platform usage analysis.

### Camera publisher

The camera publisher turns raw camera records into a public GeoJSON artifact.
It is a good first place to understand how this repository separates CLI wiring,
data ingestion, transformation, and publication contracts.

Use the fixture source when you want to try the flow locally without backend
credentials:

```bash
uv run pyro-analytics pyromap publish --source fixture --fixture-path packages/pyromap/tests/fixtures/api-cameras.json --output camera-cells.geojson
```

This command writes `camera-cells.geojson`, a shareable artifact that groups
cameras into deterministic H3 cells. Singleton camera cells are shifted to
neighboring cells by default so the public artifact avoids exposing exact source
locations. Set `CAMERA_MAP_SINGLETON_CELL_SHIFT_SALT` in production to control
the deterministic shift.

For API-backed publishing, configure backend ingestion with dlt environment
variables. S3-compatible settings, MinIO notes, object key policy, and the manual
runbook live in [docs/camera-publisher-runbook.md](docs/camera-publisher-runbook.md).

The Pyronear API source contract lives in [docs/pyronear-api.md](docs/pyronear-api.md). The public artifact contract lives in [docs/pyromap-artifact-contract.md](docs/pyromap-artifact-contract.md).

## Examples

### Camera demo data

The repository includes demo camera artifacts for contributors who want to look
at real shapes before changing code. They are synthetic, but intentionally
larger than the small unit-test fixtures:

- `examples/cameras/demo-api-cameras.json`: synthetic API-style camera records.
- `examples/cameras/demo-camera-cells.geojson`: generated public camera-cell artifact.

The demo source contains 66 synthetic camera records across fire-prone forest
regions in France, Spain, and Germany, with dense cells containing 2, 3, and 4
cameras. It is useful when reviewing map behavior, privacy-preserving cell
shifts, or the shape of the published GeoJSON.

To regenerate a local artifact from a small fixture while iterating:

```bash
uv run pyro-analytics pyromap publish --source fixture --fixture-path packages/pyromap/tests/fixtures/api-cameras.json --output camera-cells.geojson
```

Useful contribution paths from here:

- Add a new analysis package under `packages/*` for telemetry or platform usage data.
- Extend `packages/sources` with a reusable backend data source.
- Add example datasets that make a new analysis flow easy to inspect locally.
- Improve docs with screenshots, expected outputs, or operational caveats from real deployments.

## Documentation

Project documentation lives in [docs](docs/index.md). Start with the camera publisher runbook when working on operational publication flows, then use the API and artifact contracts to understand the data boundaries.

Build the Furo documentation locally with:

```bash
make build-docs
```

## Contributing

Contributions are welcome across data ingestion, telemetry analysis, operational reporting, documentation, and repository tooling. Until a dedicated `CONTRIBUTING.md` exists, use the checks below before opening a pull request.

### Workspace layout

- `src/analytics/`: repository CLI package and Typer app entrypoint
- `packages/`: workspace packages, added as `packages/*`
- `packages/sources/`: reusable dlt source definitions for backend ingestion
- `packages/pyromap/`: Pyromap ingestion execution, transformation, and publication code
- `tests/`: root CLI and workspace configuration tests
- `pyproject.toml`: lint/type/test/coverage configuration

The root `analytics` package is command wiring only. Domain implementation belongs in workspace members under `packages/*`.

### Quality checks

Common contributor commands:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest --cov=analytics --cov=sources --cov=pyromap
uv run pyro-analytics --help
```

Ruff remains strict with `target-version = "py312"`, mypy strict settings are enabled by default, and coverage is configured with branch tracking for the root CLI package and workspace package source filtering. If you relax any strictness defaults, document the rationale in this README to keep team expectations explicit.

### Continuous integration

GitHub Actions runs four independent checks on pull requests and pushes to `main`:

- `format`: `uv run ruff format . --check`
- `lint`: `uv run ruff check .`
- `type`: `uv run mypy`
- `test`: `uv run pytest`

Each job installs the locked workspace with `uv` on Python 3.13, matching the supported runtime range declared in `pyproject.toml`.

## Credits

This project is developed and maintained by Pyronear contributors and volunteers working on open wildfire monitoring infrastructure.
