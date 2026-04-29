"""Tests for camera configuration and location policy."""

from __future__ import annotations

from pathlib import Path

import pytest
from pyromap import Config, LocationPolicy


def test_default_config_uses_safe_location_policy() -> None:
    """Defaults should match the approved initial public contract."""
    config = Config()

    assert config.publish_resolution == 5
    assert config.public_properties == ("cell", "camera_count", "camera_count_bucket")
    assert config.s3_object_key == "camera-cells.geojson"
    assert config.singleton_cell_shift_enabled is True
    assert config.ingestion_pipeline_name == "pyromap"
    assert config.ingestion_dataset_name == "pyromap_data"
    assert config.ingestion_destination == "duckdb"
    assert config.ingestion_pipelines_dir == Path(".cache/pyromap/dlt-pipelines")


def test_from_env_loads_api_fixture_policy_and_minio_settings() -> None:
    """Environment loading should cover API, fixture, privacy, and S3 settings."""
    config = Config.from_env({
        "CAMERA_MAP_FIXTURE_PATH": "packages/pyromap/tests/fixtures/api-cameras.json",
        "PYROMAP_DLT_PIPELINE_NAME": "pyromap-local",
        "PYROMAP_DLT_DATASET_NAME": "pyromap_local_data",
        "PYROMAP_DLT_DESTINATION": "duckdb",
        "PYROMAP_DLT_PIPELINES_DIR": ".cache/pyromap/test-dlt-pipelines",
        "CAMERA_MAP_H3_RESOLUTION": "5",
        "CAMERA_MAP_PUBLIC_PROPERTIES": "cell, camera_count, camera_count_bucket",
        "CAMERA_MAP_S3_ENDPOINT_URL": "http://localhost:9000",
        "CAMERA_MAP_S3_REGION": "us-east-1",
        "CAMERA_MAP_S3_BUCKET": "pyronear-public-map-local",
        "CAMERA_MAP_S3_OBJECT_KEY": "camera-cells.geojson",
        "CAMERA_MAP_S3_ACCESS_KEY_ID": "minio-access",
        "CAMERA_MAP_S3_SECRET_ACCESS_KEY": "minio-secret",
        "CAMERA_MAP_SINGLETON_CELL_SHIFT_ENABLED": "false",
        "CAMERA_MAP_SINGLETON_CELL_SHIFT_SALT": "fixture-cell-shift",
    })

    assert config.fixture_path == Path("packages/pyromap/tests/fixtures/api-cameras.json")
    assert config.ingestion_pipeline_name == "pyromap-local"
    assert config.ingestion_dataset_name == "pyromap_local_data"
    assert config.ingestion_destination == "duckdb"
    assert config.ingestion_pipelines_dir == Path(".cache/pyromap/test-dlt-pipelines")
    assert config.publish_resolution == 5
    assert config.public_properties == ("cell", "camera_count", "camera_count_bucket")
    assert config.s3_endpoint_url == "http://localhost:9000"
    assert config.s3_region == "us-east-1"
    assert config.s3_bucket == "pyronear-public-map-local"
    assert config.singleton_cell_shift_enabled is False
    assert config.singleton_cell_shift_salt is not None
    assert config.singleton_cell_shift_salt.get_secret_value() == "fixture-cell-shift"
    config.require_upload_settings()


def test_invalid_h3_resolution_fails_clearly() -> None:
    """Invalid H3 resolutions should fail during config creation."""
    with pytest.raises(ValueError, match="between 0 and 15"):
        LocationPolicy(resolution=16)


def test_non_integer_env_resolution_fails_clearly() -> None:
    """Non-integer env resolution should fail with the env var name."""
    with pytest.raises(ValueError, match="CAMERA_MAP_H3_RESOLUTION"):
        Config.from_env({"CAMERA_MAP_H3_RESOLUTION": "coarse"})


def test_invalid_env_singleton_shift_flag_fails_clearly() -> None:
    """Singleton shift flag should only accept boolean-like values."""
    with pytest.raises(ValueError, match="CAMERA_MAP_SINGLETON_CELL_SHIFT_ENABLED"):
        Config.from_env({"CAMERA_MAP_SINGLETON_CELL_SHIFT_ENABLED": "sometimes"})


def test_unapproved_public_properties_fail_clearly() -> None:
    """Raw coordinate fields should not be configurable as public properties."""
    with pytest.raises(ValueError, match="lat"):
        LocationPolicy(public_properties=("cell", "lat"))


def test_missing_upload_settings_fail_before_upload() -> None:
    """Upload settings should be validated before future publisher calls."""
    config = Config(s3_bucket="pyronear-public-map-local")

    with pytest.raises(ValueError, match="CAMERA_MAP_S3_ENDPOINT_URL"):
        config.require_upload_settings()


def test_object_key_preserves_no_path_versioning_decision() -> None:
    """Config should keep the stable unversioned object key."""
    with pytest.raises(ValueError, match=r"camera-cells\.geojson"):
        Config(s3_object_key="v1/camera-cells.geojson")
