"""Deterministic camera artifact serialization helpers."""

from __future__ import annotations

import orjson
import polars as pl
from geojson_pydantic import FeatureCollection

from cameras.geojson import build_feature_collection


def serialize_feature_collection(feature_collection: FeatureCollection) -> bytes:
    """Serialize a GeoJSON FeatureCollection with stable JSON formatting."""
    payload = feature_collection.model_dump(mode="json", exclude_none=True)
    return orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)


def serialize_aggregates(aggregates: pl.DataFrame) -> bytes:
    """Build and serialize camera aggregate GeoJSON."""
    return serialize_feature_collection(build_feature_collection(aggregates))
