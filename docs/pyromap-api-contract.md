# Pyronear API Source Contract Notes

The backend dlt source follows the current Pyronear Alert API camera read contract:

- Base URL is configured in `.dlt/config.toml`.
- Bearer token is configured in `.dlt/secrets.toml`.
- Camera records are fetched with `GET /api/v1/cameras/`.
- The endpoint returns a JSON array of `CameraRead` records.
- PyroMap validates ingested records as `pyromap.Camera` before transformation.

The source does not call `GET /api/v1/login/validate` before fetching cameras. It lets the cameras endpoint return the authoritative HTTP status so tests and future CLI output can report a single failure point.

Current contract assumptions:

- `pyronear_api_base_url` may be either the API host root, such as `https://alertapi.pyronear.org`, or the versioned API root ending in `/api/v1`.
- Only trustable cameras are fetched by default. The OpenAPI contract exposes `include_non_trustable=false` on `GET /api/v1/cameras/`; camera map publication keeps that default until product requirements say otherwise.
- Raw `CameraRead` payloads are private source data. Exact `lat` and `lon` fields may exist at this boundary but must not be serialized to public artifacts.

References:

- Pyronear Alert API OpenAPI: `https://alertapi.pyronear.org/api/v1/openapi.json`
- Pyroclient route behavior: `https://pyronear.org/pyro-api/_modules/pyroclient/client.html`
