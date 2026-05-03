# Pyronear API

The backend dlt source ingests camera records from the Pyronear Alert API.

The currently implemented resource is `cameras`. It is reusable source-system
ingestion code and must not contain Pyromap transformation, privacy, GeoJSON, or
publication behavior.

## Configuration

Backend source configuration is provided through dlt-compatible environment
variables:

| Variable | Purpose | Secret |
| --- | --- | --- |
| `SOURCES__BACKEND__PYRONEAR_API_BASE_URL` | Pyronear Alert API base URL | No |
| `SOURCES__BACKEND__PYRONEAR_API_TOKEN` | Bearer token for camera reads | Yes |

`pyronear_api_base_url` may be either the API host root, such as
`https://alertapi.pyronear.org`, or the versioned API root ending in `/api/v1`.

## Endpoint

Camera records are fetched with:

```text
GET /api/v1/cameras/
```

The endpoint is expected to return a JSON array of `CameraRead` records.
Only trustable cameras are fetched by default. The OpenAPI contract exposes
`include_non_trustable=false` on `GET /api/v1/cameras/`; publication workflows
keep that default until product requirements say otherwise.

## Authentication

The source uses bearer authentication through the dlt REST API source
configuration. It does not construct raw `Authorization` headers in workflow
code.

The source does not call `GET /api/v1/login/validate` before fetching cameras.
It lets the cameras endpoint return the authoritative HTTP status so tests and
future CLI output can report a single failure point.

## Private Data Boundary

Raw `CameraRead` payloads are private source data. Exact `lat` and `lon` fields
may exist at this boundary but must not be serialized to public artifacts.

Pyromap validates ingested camera rows as `pyromap.Camera` before transforming
them into public H3 cells.

## References

- Pyronear Alert API OpenAPI: `https://alertapi.pyronear.org/api/v1/openapi.json`
- Pyroclient route behavior: `https://pyronear.org/pyro-api/_modules/pyroclient/client.html`
