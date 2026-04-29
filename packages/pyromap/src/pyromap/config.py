"""Configuration models for camera map publishing."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from pyromap.privacy import DEFAULT_LOCATION_POLICY, LocationPolicy


def _optional_env(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None
    stripped_value = value.strip()
    return stripped_value or None


def _optional_secret(environ: Mapping[str, str], name: str) -> SecretStr | None:
    value = _optional_env(environ, name)
    if value is None:
        return None
    return SecretStr(value)


def _optional_path(environ: Mapping[str, str], name: str) -> Path | None:
    value = _optional_env(environ, name)
    if value is None:
        return None
    return Path(value)


def _env_bool(environ: Mapping[str, str], name: str, *, default: bool) -> bool:
    value = _optional_env(environ, name)
    if value is None:
        return default

    normalized_value = value.casefold()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False

    msg = f"{name} must be a boolean value."
    raise ValueError(msg)


def _env_resolution(environ: Mapping[str, str]) -> int:
    value = _optional_env(environ, "CAMERA_MAP_H3_RESOLUTION")
    if value is None:
        return DEFAULT_LOCATION_POLICY.resolution
    try:
        return int(value)
    except ValueError as exc:
        msg = "CAMERA_MAP_H3_RESOLUTION must be an integer."
        raise ValueError(msg) from exc


def _env_public_properties(environ: Mapping[str, str]) -> tuple[str, ...]:
    value = _optional_env(environ, "CAMERA_MAP_PUBLIC_PROPERTIES")
    if value is None:
        return DEFAULT_LOCATION_POLICY.public_properties

    properties = tuple(part.strip() for part in value.split(",") if part.strip())
    if not properties:
        return DEFAULT_LOCATION_POLICY.public_properties
    return properties


class Config(BaseModel):
    """Typed camera publisher configuration."""

    model_config = ConfigDict(frozen=True)

    fixture_path: Path | None = None
    ingestion_pipeline_name: str = "pyromap"
    ingestion_dataset_name: str = "pyromap_data"
    ingestion_destination: str = "duckdb"
    ingestion_pipelines_dir: Path = Path(".cache/pyromap/dlt-pipelines")
    location_policy: LocationPolicy = Field(default_factory=lambda: DEFAULT_LOCATION_POLICY)
    s3_endpoint_url: str | None = None
    s3_region: str | None = None
    s3_bucket: str | None = None
    s3_object_key: str = "camera-cells.geojson"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    singleton_cell_shift_enabled: bool = True
    singleton_cell_shift_salt: SecretStr | None = None

    @field_validator("s3_object_key")
    @classmethod
    def validate_object_key(cls, value: str) -> str:
        """Ensure the configured object key is usable and unversioned."""
        stripped_value = value.strip()
        if not stripped_value:
            msg = "s3_object_key must be non-empty."
            raise ValueError(msg)
        if stripped_value != "camera-cells.geojson":
            msg = "s3_object_key must remain camera-cells.geojson."
            raise ValueError(msg)
        return stripped_value

    @property
    def publish_resolution(self) -> int:
        """Approved H3 publish resolution."""
        return self.location_policy.resolution

    @property
    def public_properties(self) -> tuple[str, ...]:
        """Allowed public feature properties."""
        return self.location_policy.public_properties

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Config:
        """Load camera configuration from environment variables."""
        source = os.environ if environ is None else environ
        location_policy = LocationPolicy(
            resolution=_env_resolution(source),
            public_properties=_env_public_properties(source),
        )

        return cls(
            fixture_path=_optional_path(source, "CAMERA_MAP_FIXTURE_PATH"),
            ingestion_pipeline_name=_optional_env(source, "PYROMAP_DLT_PIPELINE_NAME") or "pyromap",
            ingestion_dataset_name=_optional_env(source, "PYROMAP_DLT_DATASET_NAME") or "pyromap_data",
            ingestion_destination=_optional_env(source, "PYROMAP_DLT_DESTINATION") or "duckdb",
            ingestion_pipelines_dir=_optional_path(source, "PYROMAP_DLT_PIPELINES_DIR")
            or Path(".cache/pyromap/dlt-pipelines"),
            location_policy=location_policy,
            s3_endpoint_url=_optional_env(source, "CAMERA_MAP_S3_ENDPOINT_URL"),
            s3_region=_optional_env(source, "CAMERA_MAP_S3_REGION"),
            s3_bucket=_optional_env(source, "CAMERA_MAP_S3_BUCKET"),
            s3_object_key=_optional_env(source, "CAMERA_MAP_S3_OBJECT_KEY") or "camera-cells.geojson",
            s3_access_key_id=_optional_secret(source, "CAMERA_MAP_S3_ACCESS_KEY_ID"),
            s3_secret_access_key=_optional_secret(source, "CAMERA_MAP_S3_SECRET_ACCESS_KEY"),
            singleton_cell_shift_enabled=_env_bool(source, "CAMERA_MAP_SINGLETON_CELL_SHIFT_ENABLED", default=True),
            singleton_cell_shift_salt=_optional_secret(source, "CAMERA_MAP_SINGLETON_CELL_SHIFT_SALT"),
        )

    def require_upload_settings(self) -> None:
        """Fail before upload when required S3-compatible settings are missing."""
        required_settings = {
            "CAMERA_MAP_S3_ENDPOINT_URL": self.s3_endpoint_url,
            "CAMERA_MAP_S3_REGION": self.s3_region,
            "CAMERA_MAP_S3_BUCKET": self.s3_bucket,
            "CAMERA_MAP_S3_ACCESS_KEY_ID": self.s3_access_key_id,
            "CAMERA_MAP_S3_SECRET_ACCESS_KEY": self.s3_secret_access_key,
        }
        missing_settings = [name for name, value in required_settings.items() if value is None]
        if missing_settings:
            joined_settings = ", ".join(missing_settings)
            msg = f"Missing required upload settings: {joined_settings}."
            raise ValueError(msg)
