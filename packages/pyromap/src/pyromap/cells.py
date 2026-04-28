"""Cell indexing and boundary helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

import h3  # type: ignore[import-untyped]
import polars as pl
import polars_h3 as ph3  # type: ignore[import-untyped]

from pyromap.config import Config
from pyromap.schemas import Camera, CellProperties

CAMERA_FRAME_SCHEMA = {
    "camera_id": pl.Int64,
    "lat": pl.Float64,
    "lon": pl.Float64,
}
AGGREGATE_SCHEMA = {
    "cell": pl.Utf8,
    "camera_count": pl.Int64,
    "camera_count_bucket": pl.Utf8,
}
DEFAULT_SINGLETON_CELL_SHIFT_SALT = "pyronear-camera-map-singleton-cell-shift"


def cameras_to_frame(cameras: Iterable[Camera]) -> pl.DataFrame:
    """Convert typed camera records into a private Polars frame."""
    rows = [{"camera_id": camera.id, "lat": camera.lat, "lon": camera.lon} for camera in cameras]
    return pl.DataFrame(rows, schema=CAMERA_FRAME_SCHEMA)


def _validate_coordinates(frame: pl.DataFrame) -> None:
    invalid_coordinates = frame.filter(
        pl.col("lat").is_null()
        | pl.col("lon").is_null()
        | (pl.col("lat") < -90)
        | (pl.col("lat") > 90)
        | (pl.col("lon") < -180)
        | (pl.col("lon") > 180)
    )
    if not invalid_coordinates.is_empty():
        msg = "camera coordinates must be present and within valid ranges before H3 indexing."
        raise ValueError(msg)


def _shifted_singleton_cell(cell: str, config: Config) -> str:
    neighbors = sorted(str(neighbor) for neighbor in h3.grid_disk(cell, 1) if neighbor != cell)
    if not neighbors:
        return cell

    salt = (
        config.singleton_cell_shift_salt.get_secret_value()
        if config.singleton_cell_shift_salt is not None
        else DEFAULT_SINGLETON_CELL_SHIFT_SALT
    )
    digest = hashlib.sha256(f"{salt}:{cell}".encode()).digest()
    index = int.from_bytes(digest[:8], "big") % len(neighbors)
    return neighbors[index]


def _camera_count_bucket_expr() -> pl.Expr:
    return (
        pl
        .when(pl.col("camera_count") == 1)
        .then(pl.lit("1"))
        .when(pl.col("camera_count") <= 5)
        .then(pl.lit("2-5"))
        .when(pl.col("camera_count") <= 10)
        .then(pl.lit("6-10"))
        .otherwise(pl.lit("10+"))
        .alias("camera_count_bucket")
    )


def _shift_singleton_cells(aggregates: pl.DataFrame, config: Config) -> pl.DataFrame:
    rows: list[dict[str, str | int]] = []
    for row in aggregates.iter_rows(named=True):
        cell = str(row["cell"])
        camera_count = int(row["camera_count"])
        public_cell = cell
        if config.singleton_cell_shift_enabled and camera_count == 1:
            public_cell = _shifted_singleton_cell(cell, config)
        rows.append({"cell": public_cell, "camera_count": camera_count})

    return pl.DataFrame(rows, schema={"cell": pl.Utf8, "camera_count": pl.Int64})


def index_cameras(frame: pl.DataFrame, *, resolution: int) -> pl.DataFrame:
    """Compute H3 cells for camera coordinates and drop raw coordinates."""
    if frame.is_empty():
        return pl.DataFrame(schema={"camera_id": pl.Int64, "cell": pl.Utf8})

    _validate_coordinates(frame)
    return frame.with_columns(ph3.latlng_to_cell("lat", "lon", resolution, return_dtype=pl.Utf8).alias("cell")).drop(
        "lat", "lon"
    )


def aggregate_cells(cameras: Iterable[Camera], config: Config) -> pl.DataFrame:
    """Aggregate cameras into public H3 cell properties."""
    selected_properties = list(config.public_properties)
    frame = cameras_to_frame(cameras)
    if frame.is_empty():
        return pl.DataFrame(schema={name: AGGREGATE_SCHEMA[name] for name in selected_properties})

    indexed = index_cameras(frame, resolution=config.publish_resolution)
    source_aggregates = indexed.group_by("cell").agg(pl.len().alias("camera_count"))
    public_aggregates = _shift_singleton_cells(source_aggregates, config)
    aggregates = (
        public_aggregates
        .group_by("cell")
        .agg(pl.sum("camera_count").alias("camera_count"))
        .with_columns(_camera_count_bucket_expr())
        .sort("cell")
        .select(*AGGREGATE_SCHEMA)
    )

    for row in aggregates.iter_rows(named=True):
        CellProperties.model_validate(row)
    return aggregates.select(selected_properties)
