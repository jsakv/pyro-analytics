# Pyromap

```{toctree}
:maxdepth: 2
:hidden:

Contracts <pyromap-contracts>
Runbooks <pyromap-runbooks>
```

Pyromap publishes camera coverage data as a privacy-aware GeoJSON artifact for
map consumers.

The workflow is intentionally split into clear boundaries:

- `sources` defines the reusable Pyronear API dlt source.
- `pyromap.ingestion` runs dlt ingestion for backend camera records.
- Pyromap transformation code reads typed records, aggregates H3 cells, and
  applies privacy rules outside dlt.
- Pyromap publishers write the stable `camera-cells.geojson` artifact locally or
  to S3-compatible storage.

Use fixture mode for local development and tests. It reads synthetic camera
records directly and bypasses dlt because fixture data is local demo input, not
a production source.

Use API mode for production publication. It runs backend camera ingestion through
dlt, reads the ingested rows, transforms them into public cells, and publishes
the artifact.

For stable output behavior, see [Contracts](pyromap-contracts.md). For manual
publishing steps, see [Runbooks](pyromap-runbooks.md).
