"""GeoJSON construction and validation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import h3  # type: ignore[import-untyped]
import polars as pl
from geojson_pydantic import Feature, FeatureCollection

from cameras.schemas import CellProperties

Position = list[float]


def cell_boundary(cell: str) -> list[Position]:
    """Return a closed GeoJSON ring for an H3 cell."""
    if not h3.is_valid_cell(cell):
        msg = f"invalid H3 cell: {cell}."
        raise ValueError(msg)

    ring = [[lng, lat] for lat, lng in h3.cell_to_boundary(cell)]
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return ring


def build_feature_collection(aggregates: pl.DataFrame) -> FeatureCollection:
    """Build and validate a public GeoJSON FeatureCollection."""
    features = [_build_feature(row) for row in _sorted_rows(aggregates)]
    return FeatureCollection.model_validate({"type": "FeatureCollection", "features": features})


def _build_feature(row: Mapping[str, Any]) -> Feature:
    properties = CellProperties.model_validate(row).model_dump(mode="json")
    return Feature.model_validate({
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [cell_boundary(properties["cell"])],
        },
        "properties": properties,
    })


def _sorted_rows(aggregates: pl.DataFrame) -> list[dict[str, Any]]:
    rows = aggregates.to_dicts()
    return sorted(rows, key=lambda row: str(row.get("cell", "")))
