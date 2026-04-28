"""dlt source definitions for the Pyronear backend API."""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources

DEFAULT_API_BASE_URL = "https://alertapi.pyronear.org/api/v1/"


def normalize_api_base_url(api_base_url: str) -> str:
    """Return a base URL suitable for the backend API v1 resources."""
    stripped_base = api_base_url.rstrip("/")
    if stripped_base.endswith("/api/v1"):
        return f"{stripped_base}/"
    return f"{stripped_base}/api/v1/"


def backend_rest_api_config(*, pyronear_api_base_url: str, pyronear_api_token: str) -> RESTAPIConfig:
    """Build the declarative REST API config for backend ingestion."""
    return {
        "client": {
            "base_url": normalize_api_base_url(pyronear_api_base_url),
            "auth": {
                "type": "bearer",
                "token": pyronear_api_token,
            },
        },
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "replace",
        },
        "resources": [
            {
                "name": "cameras",
                "endpoint": {
                    "path": "cameras/",
                    "data_selector": "$",
                },
            },
        ],
    }


@dlt.source(name="backend")
def backend_source(
    pyronear_api_base_url: str = dlt.config.value,
    pyronear_api_token: str = dlt.secrets.value,
) -> Iterator[object]:
    """Expose backend API resources for ingestion."""
    yield from rest_api_resources(
        backend_rest_api_config(
            pyronear_api_base_url=pyronear_api_base_url,
            pyronear_api_token=pyronear_api_token,
        )
    )
