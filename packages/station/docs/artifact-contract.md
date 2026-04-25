# Station Artifact Contract

The station publisher produces one public GeoJSON artifact for the public map:

```text
station-cells.geojson
```

The object key is stable across environments. Environment separation belongs in bucket configuration, not in path versioning.

## Source Fixture

`packages/station/tests/fixtures/api-cameras.json` is synthetic data shaped like the `GET /api/v1/cameras/` response from the Pyronear Alert API. It mocks the API boundary used by the station source adapter so tests can run without live credentials.

The fixture is not a database fixture and must not expose database-only fields. It contains plausible `CameraRead` fields from the OpenAPI contract, including exact coordinates because source data is still private at this boundary.

## Public Artifact Fixture

`packages/station/tests/fixtures/station-cells.geojson` is synthetic public output. It is safe for downstream map tests and must not contain raw station identifiers, station names, exact coordinates, image URLs, backend URLs, credentials, or source payload fragments.

Each public feature is a GeoJSON polygon with this property allowlist:

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| `cell` | string | Yes | H3 cell identifier at the configured publish resolution. |
| `station_count` | integer | Yes | Number of valid source stations aggregated into the cell. |
| `station_count_bucket` | string | Yes | Coarse density bucket derived from `station_count`. |

Initial bucket labels are `1`, `2-5`, `6-10`, and `10+`.

Any feature property change is a cross-repository contract change with `pyro-map`.
