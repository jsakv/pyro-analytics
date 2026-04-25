# Pyronear Station

`station` is the reusable publisher library for Pyronear station map artifacts.

The package owns source adapters, schema validation, location privacy policy, H3 aggregation, GeoJSON serialization, and publication boundaries for station map data. The root `analytics` package owns CLI wiring and may depend on `station`; `station` must not import from `analytics`.

Use the root CLI for operational publishing:

```bash
uv run analytics station publish --source fixture --fixture-path packages/station/tests/fixtures/api-cameras.json --output station-cells.geojson
```

See [docs/artifact-contract.md](docs/artifact-contract.md) for the source and public artifact fixture contracts, and [../../docs/station-publisher-runbook.md](../../docs/station-publisher-runbook.md) for the manual publish runbook.
