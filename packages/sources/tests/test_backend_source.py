"""Tests for the Pyronear backend dlt source definition."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from sources.backend import backend_rest_api_config, backend_source, normalize_api_base_url

ROOT = Path(__file__).parents[3]


def test_backend_source_exposes_only_cameras_resource() -> None:
    """The first migration should expose backend cameras only."""
    backend = backend_source(
        pyronear_api_base_url="https://alertapi.pyronear.org",
        pyronear_api_token="synthetic-token",  # noqa: S106
    )

    assert list(backend.resources.keys()) == ["cameras"]


def test_backend_rest_api_config_uses_cameras_endpoint_and_bearer_auth() -> None:
    """REST API source config should match the backend camera contract."""
    config = cast(
        Any,
        backend_rest_api_config(
            pyronear_api_base_url="https://alertapi.pyronear.org",
            pyronear_api_token="synthetic-token",  # noqa: S106
        ),
    )

    assert config["client"]["base_url"] == "https://alertapi.pyronear.org/api/v1/"
    assert config["client"]["auth"] == {"type": "bearer", "token": "synthetic-token"}
    assert config["resource_defaults"]["primary_key"] == "id"
    assert config["resource_defaults"]["write_disposition"] == "replace"
    assert config["resources"] == [
        {
            "name": "cameras",
            "endpoint": {
                "path": "cameras/",
                "data_selector": "$",
            },
        },
    ]


def test_backend_base_url_accepts_api_root_or_versioned_root() -> None:
    """Configured backend URLs may include or omit the API version prefix."""
    assert normalize_api_base_url("https://alertapi.pyronear.org") == "https://alertapi.pyronear.org/api/v1/"
    assert normalize_api_base_url("https://alertapi.pyronear.org/api/v1") == "https://alertapi.pyronear.org/api/v1/"


def test_frontend_and_crm_packages_are_not_implemented() -> None:
    """Frontend and CRM sources are intentionally out of scope."""
    assert not (ROOT / "packages" / "sources" / "src" / "sources" / "frontend").exists()
    assert not (ROOT / "packages" / "sources" / "src" / "sources" / "crm").exists()
