"""Typed schemas for camera source records and public artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RAW_COORDINATE_FIELDS = frozenset({"lat", "latitude", "lon", "lng", "longitude"})


def _reject_raw_coordinate_fields(value: Any) -> Any:
    if not isinstance(value, Mapping):
        return value

    raw_fields = RAW_COORDINATE_FIELDS.intersection(value)
    if raw_fields:
        joined_fields = ", ".join(sorted(raw_fields))
        msg = f"raw coordinate fields are not public properties: {joined_fields}."
        raise ValueError(msg)
    return value


class Pose(BaseModel):
    """Source pose record nested inside a camera payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    azimuth: float | None = None
    patrol_id: int | None = None
    id: int
    camera_id: int


class Camera(BaseModel):
    """Private source camera record with exact coordinates."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: int
    name: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    elevation: float | None = None
    organization_id: int
    angle_of_view: float | None = None
    is_trustable: bool
    last_active_at: datetime | None = None
    last_image: str | None = None
    created_at: datetime
    poses: tuple[Pose, ...] = Field(default_factory=tuple)
    last_image_url: str | None = None


class CellProperties(BaseModel):
    """Public properties for one aggregated camera cell."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cell: str = Field(min_length=1)
    camera_count: int = Field(ge=1)
    camera_count_bucket: Literal["1", "2-5", "6-10", "10+"]

    @model_validator(mode="before")
    @classmethod
    def reject_raw_coordinate_fields(cls, value: Any) -> Any:
        """Keep exact coordinates out of the public artifact boundary."""
        return _reject_raw_coordinate_fields(value)


class Result(BaseModel):
    """Outcome metadata returned by camera publication."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    camera_count: int = Field(default=0, ge=0)
    cell_count: int = Field(default=0, ge=0)
    artifact_key: str = Field(default="camera-cells.geojson", min_length=1)
    published: bool = False
    bucket: str | None = None
    endpoint_url: str | None = None
    etag: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_raw_coordinate_fields(cls, value: Any) -> Any:
        """Keep result metadata free of exact coordinates."""
        return _reject_raw_coordinate_fields(value)
