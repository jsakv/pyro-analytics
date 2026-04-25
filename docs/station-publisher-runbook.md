# Station Publisher Runbook

This runbook is for maintainers publishing the public station map artifact from `pyro-analytics`.

## Artifact Contract

The publisher writes one public GeoJSON artifact:

```text
station-cells.geojson
```

The object key is intentionally stable and unversioned. Environment separation belongs in bucket configuration, not path prefixes or timestamped object names. This keeps the `pyro-map` consumer contract simple and cache behavior explicit.

Public features may contain only:

- `cell`
- `station_count`
- `station_count_bucket`

Raw station coordinates and private source fields must never be published. Do not publish `lat`, `lon`, station names, station IDs, organization IDs, image URLs, backend URLs, credentials, or raw API records.

## Location Precision Review

The default public precision is H3 resolution `5`. Review this before production release and whenever station density materially changes.

Review checklist:

- Confirm the configured `STATION_MAP_H3_RESOLUTION` is coarse enough for the target geography.
- Confirm `STATION_MAP_PUBLIC_PROPERTIES` stays within the approved property allowlist.
- Inspect a generated fixture artifact before uploading.
- Treat any property change as a cross-repository contract change with `pyro-map`.

## Local Fixture Publish

Use the synthetic fixture path for local validation and CI-like checks. This does not call `pyro-api` or S3.

```bash
uv sync
uv run analytics station publish \
  --source fixture \
  --fixture-path packages/station/tests/fixtures/api-cameras.json \
  --output station-cells.geojson
```

Expected output shape:

```text
fetched=3 published=2 uploaded=1 artifact=station-cells.geojson
```

For a larger demo map, use the example dataset:

```bash
uv run analytics station publish \
  --source fixture \
  --fixture-path examples/station/demo-api-cameras.json \
  --output station-cells.geojson
```

Before sharing the artifact, inspect it for private fields:

```bash
rg '"lat"|"lon"|"name"|"organization_id"|"last_image"' station-cells.geojson
```

The search should return no matches.

## API To S3 Publish

Production publishing uses the API source and S3-compatible publisher:

```bash
PYRONEAR_API_URL=https://alertapi.pyronear.org \
PYRONEAR_API_TOKEN=<token> \
STATION_MAP_S3_ENDPOINT_URL=<s3-endpoint-url> \
STATION_MAP_S3_REGION=<region> \
STATION_MAP_S3_BUCKET=<bucket> \
STATION_MAP_S3_ACCESS_KEY_ID=<access-key-id> \
STATION_MAP_S3_SECRET_ACCESS_KEY=<secret-access-key> \
uv run analytics station publish --source api
```

Required settings:

| Variable | Purpose | Secret |
| --- | --- | --- |
| `PYRONEAR_API_URL` | Pyronear Alert API base URL | No |
| `PYRONEAR_API_TOKEN` | Bearer token for camera reads | Yes |
| `STATION_MAP_H3_RESOLUTION` | Optional H3 publish resolution, default `5` | No |
| `STATION_MAP_PUBLIC_PROPERTIES` | Optional comma-separated public fields | No |
| `STATION_MAP_S3_ENDPOINT_URL` | S3 or MinIO-compatible endpoint URL | No |
| `STATION_MAP_S3_REGION` | S3 region name | No |
| `STATION_MAP_S3_BUCKET` | Target bucket | No |
| `STATION_MAP_S3_OBJECT_KEY` | Stable key, must be `station-cells.geojson` | No |
| `STATION_MAP_S3_ACCESS_KEY_ID` | S3 access key ID | Yes |
| `STATION_MAP_S3_SECRET_ACCESS_KEY` | S3 secret access key | Yes |

Do not paste secret values into docs, issue comments, shell history, or CI logs.

## MinIO Development

For local MinIO, use the MinIO endpoint and a local bucket:

```bash
STATION_MAP_S3_ENDPOINT_URL=http://localhost:9000
STATION_MAP_S3_REGION=us-east-1
STATION_MAP_S3_BUCKET=pyronear-public-map-local
STATION_MAP_S3_OBJECT_KEY=station-cells.geojson
```

Create credentials in MinIO and provide them through `STATION_MAP_S3_ACCESS_KEY_ID` and `STATION_MAP_S3_SECRET_ACCESS_KEY`. Keep the object key unchanged.

## Failure Handling

The CLI exits non-zero for source, validation, serialization, or upload failures. Error messages should identify the failing boundary but must not include credentials or raw station payloads.

If publication fails:

1. Run the fixture publish command locally.
2. Run the local validation suite:

   ```bash
   uv run ruff format . --check
   uv run ruff check .
   uv run mypy
   uv run pytest
   ```

3. Verify API token scope and expiry.
4. Verify S3/MinIO endpoint, bucket, and credentials.
5. Re-run the publish command after the failing boundary is fixed.

No automated schedule is configured yet. Add scheduling only after the refresh cadence and ownership are confirmed.
