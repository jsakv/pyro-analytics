"""Tests for station configuration and location policy."""

from __future__ import annotations

from pathlib import Path

import pytest
from station import Config, LocationPolicy


def test_default_config_uses_safe_location_policy() -> None:
    """Defaults should match the approved initial public contract."""
    config = Config()

    assert config.publish_resolution == 5
    assert config.public_properties == ("cell", "station_count", "station_count_bucket")
    assert config.s3_object_key == "station-cells.geojson"


def test_from_env_loads_api_fixture_policy_and_minio_settings() -> None:
    """Environment loading should cover API, fixture, privacy, and S3 settings."""
    config = Config.from_env({
        "PYRONEAR_API_URL": "https://alertapi.pyronear.org",
        "PYRONEAR_API_TOKEN": "synthetic-token",
        "STATION_MAP_FIXTURE_PATH": "packages/station/tests/fixtures/api-cameras.json",
        "STATION_MAP_H3_RESOLUTION": "5",
        "STATION_MAP_PUBLIC_PROPERTIES": "cell, station_count, station_count_bucket",
        "STATION_MAP_S3_ENDPOINT_URL": "http://localhost:9000",
        "STATION_MAP_S3_REGION": "us-east-1",
        "STATION_MAP_S3_BUCKET": "pyronear-public-map-local",
        "STATION_MAP_S3_OBJECT_KEY": "station-cells.geojson",
        "STATION_MAP_S3_ACCESS_KEY_ID": "minio-access",
        "STATION_MAP_S3_SECRET_ACCESS_KEY": "minio-secret",
    })

    assert config.api_url == "https://alertapi.pyronear.org"
    assert config.api_token is not None
    assert config.api_token.get_secret_value() == "synthetic-token"
    assert config.fixture_path == Path("packages/station/tests/fixtures/api-cameras.json")
    assert config.publish_resolution == 5
    assert config.public_properties == ("cell", "station_count", "station_count_bucket")
    assert config.s3_endpoint_url == "http://localhost:9000"
    assert config.s3_region == "us-east-1"
    assert config.s3_bucket == "pyronear-public-map-local"
    config.require_upload_settings()


def test_invalid_h3_resolution_fails_clearly() -> None:
    """Invalid H3 resolutions should fail during config creation."""
    with pytest.raises(ValueError, match="between 0 and 15"):
        LocationPolicy(resolution=16)


def test_non_integer_env_resolution_fails_clearly() -> None:
    """Non-integer env resolution should fail with the env var name."""
    with pytest.raises(ValueError, match="STATION_MAP_H3_RESOLUTION"):
        Config.from_env({"STATION_MAP_H3_RESOLUTION": "coarse"})


def test_unapproved_public_properties_fail_clearly() -> None:
    """Raw coordinate fields should not be configurable as public properties."""
    with pytest.raises(ValueError, match="lat"):
        LocationPolicy(public_properties=("cell", "lat"))


def test_missing_upload_settings_fail_before_upload() -> None:
    """Upload settings should be validated before future publisher calls."""
    config = Config(s3_bucket="pyronear-public-map-local")

    with pytest.raises(ValueError, match="STATION_MAP_S3_ENDPOINT_URL"):
        config.require_upload_settings()


def test_object_key_preserves_no_path_versioning_decision() -> None:
    """Config should keep the stable unversioned object key."""
    with pytest.raises(ValueError, match=r"station-cells\.geojson"):
        Config(s3_object_key="v1/station-cells.geojson")
