# Pyronear Cameras

`cameras` is the reusable publisher library for Pyronear camera map artifacts.

The package owns source adapters, schema validation, location privacy policy, H3 aggregation, GeoJSON serialization, and publication boundaries for camera map data. The root `analytics` package owns CLI wiring and may depend on `cameras`; `cameras` must not import from `analytics`.

Use the root CLI for operational publishing:

```bash
uv run analytics cameras publish --source fixture --fixture-path packages/cameras/tests/fixtures/api-cameras.json --output camera-cells.geojson
```

See [docs/artifact-contract.md](docs/artifact-contract.md) for the source and public artifact fixture contracts, and [../../docs/camera-publisher-runbook.md](../../docs/camera-publisher-runbook.md) for the manual publish runbook.
