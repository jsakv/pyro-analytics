"""Cell indexing and boundary helpers."""

from __future__ import annotations

from collections.abc import Iterable

import polars as pl
import polars_h3 as ph3  # type: ignore[import-untyped]

from station.config import Config
from station.schemas import CellProperties, Station

STATION_FRAME_SCHEMA = {
    "station_id": pl.Int64,
    "lat": pl.Float64,
    "lon": pl.Float64,
}
AGGREGATE_SCHEMA = {
    "cell": pl.Utf8,
    "station_count": pl.Int64,
    "station_count_bucket": pl.Utf8,
}


def stations_to_frame(stations: Iterable[Station]) -> pl.DataFrame:
    """Convert typed station records into a private Polars frame."""
    rows = [{"station_id": station.id, "lat": station.lat, "lon": station.lon} for station in stations]
    return pl.DataFrame(rows, schema=STATION_FRAME_SCHEMA)


def index_stations(frame: pl.DataFrame, *, resolution: int) -> pl.DataFrame:
    """Compute H3 cells for station coordinates and drop raw coordinates."""
    if frame.is_empty():
        return pl.DataFrame(schema={"station_id": pl.Int64, "cell": pl.Utf8})

    _validate_coordinates(frame)
    return frame.with_columns(ph3.latlng_to_cell("lat", "lon", resolution, return_dtype=pl.Utf8).alias("cell")).drop(
        "lat", "lon"
    )


def aggregate_cells(stations: Iterable[Station], config: Config) -> pl.DataFrame:
    """Aggregate stations into public H3 cell properties."""
    selected_properties = list(config.public_properties)
    frame = stations_to_frame(stations)
    if frame.is_empty():
        return pl.DataFrame(schema={name: AGGREGATE_SCHEMA[name] for name in selected_properties})

    indexed = index_stations(frame, resolution=config.publish_resolution)
    aggregates = (
        indexed
        .group_by("cell")
        .agg(pl.len().alias("station_count"))
        .with_columns(_station_count_bucket_expr())
        .sort("cell")
        .select(*AGGREGATE_SCHEMA)
    )

    for row in aggregates.iter_rows(named=True):
        CellProperties.model_validate(row)
    return aggregates.select(selected_properties)


def _station_count_bucket_expr() -> pl.Expr:
    return (
        pl
        .when(pl.col("station_count") == 1)
        .then(pl.lit("1"))
        .when(pl.col("station_count") <= 5)
        .then(pl.lit("2-5"))
        .when(pl.col("station_count") <= 10)
        .then(pl.lit("6-10"))
        .otherwise(pl.lit("10+"))
        .alias("station_count_bucket")
    )


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
        msg = "station coordinates must be present and within valid ranges before H3 indexing."
        raise ValueError(msg)
