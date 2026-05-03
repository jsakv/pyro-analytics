# Pyromap Artifact

The camera publisher produces one public GeoJSON artifact for the public map:

```text
camera-cells.geojson
```

The object key is stable across environments. Environment separation belongs in bucket configuration, not in path versioning.

This contract is the public boundary for downstream map consumers. The artifact
must not expose exact camera locations, raw source identifiers, backend URLs, or
source payload fragments.

## Public Properties

Each public feature is a GeoJSON polygon with this property allowlist:

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| `cell` | string | Yes | H3 cell identifier at the configured publish resolution. |
| `camera_count` | integer | Yes | Number of valid source cameras aggregated into the cell. |
| `camera_count_bucket` | string | Yes | Coarse density bucket derived from `camera_count`. |

Initial bucket labels are `1`, `2-5`, `6-10`, and `10+`.

Any feature property change is a cross-repository contract change with `pyro-map`.

## Privacy Exclusions

Public artifacts must not contain:

- raw `lat` or `lon` coordinates
- camera IDs
- camera names
- organization IDs
- image URLs
- backend URLs
- credentials
- raw API records

## Source Fixture

`packages/pyromap/tests/fixtures/api-cameras.json` is synthetic data shaped like the `GET /api/v1/cameras/` response from the Pyronear Alert API. It mocks the API boundary used by the camera source adapter so tests can run without live credentials.

The fixture is not a database fixture and must not expose database-only fields. It contains plausible `CameraRead` fields from the OpenAPI contract, including exact coordinates because source data is still private at this boundary.

## Public Artifact Fixture

`packages/pyromap/tests/fixtures/camera-cells.geojson` is synthetic public output. It is safe for downstream map tests and must not contain raw camera identifiers, camera names, exact coordinates, image URLs, backend URLs, credentials, or source payload fragments.
