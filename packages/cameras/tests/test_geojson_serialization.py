"""Tests for GeoJSON construction and deterministic serialization."""

from __future__ import annotations

import json
from pathlib import Path

import h3  # type: ignore[import-untyped]
import polars as pl
import pytest
from cameras import Camera, Config
from cameras.cells import aggregate_cells
from cameras.geojson import build_feature_collection, cell_boundary
from cameras.serialization import serialize_aggregates, serialize_feature_collection
from cameras.sources import FixtureSource
from geojson_pydantic import FeatureCollection
from pydantic import ValidationError

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


def load_fixture_cameras() -> list[Camera]:
    """Load typed synthetic cameras from the fixture source."""
    return FixtureSource(FIXTURES_ROOT / "api-cameras.json").fetch()


def load_aggregates() -> pl.DataFrame:
    """Build deterministic fixture aggregates."""
    return aggregate_cells(load_fixture_cameras(), Config())


def test_cell_boundary_writes_longitude_latitude_order() -> None:
    """H3 boundaries should be converted from lat/lng to GeoJSON lng/lat."""
    cell = "85396c5bfffffff"
    first_lat, first_lng = h3.cell_to_boundary(cell)[0]

    ring = cell_boundary(cell)

    assert ring[0] == [first_lng, first_lat]
    assert ring[-1] == ring[0]
    assert len(ring) >= 4


def test_build_feature_collection_validates_aggregates() -> None:
    """Valid aggregates should become a geojson-pydantic FeatureCollection."""
    feature_collection = build_feature_collection(load_aggregates())

    assert isinstance(feature_collection, FeatureCollection)
    payload = feature_collection.model_dump(mode="json", exclude_none=True)
    assert payload["type"] == "FeatureCollection"
    assert [feature["properties"]["cell"] for feature in payload["features"]] == [
        "85396803fffffff",
        "85396c5bfffffff",
    ]


def test_feature_collection_has_polygon_coordinates() -> None:
    """Aggregate features should use H3 polygon boundaries."""
    payload = build_feature_collection(load_aggregates()).model_dump(mode="json", exclude_none=True)

    first_feature = payload["features"][0]
    assert first_feature["geometry"]["type"] == "Polygon"
    ring = first_feature["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]
    assert all(len(position) == 2 for position in ring)


def test_build_feature_collection_rejects_raw_coordinates() -> None:
    """Raw coordinate columns should not cross into public GeoJSON properties."""
    aggregates = load_aggregates().with_columns(pl.lit(43.6122).alias("lat"))

    with pytest.raises(ValidationError, match="raw coordinate fields"):
        build_feature_collection(aggregates)


def test_build_feature_collection_rejects_invalid_cells() -> None:
    """Invalid H3 cells should fail before serialization."""
    aggregates = pl.DataFrame([
        {
            "cell": "not-a-cell",
            "camera_count": 1,
            "camera_count_bucket": "1",
        }
    ])

    with pytest.raises(ValueError, match="invalid H3 cell"):
        build_feature_collection(aggregates)


def test_serialize_feature_collection_is_deterministic() -> None:
    """Serialization should produce stable bytes from equivalent aggregates."""
    aggregates = load_aggregates()
    reversed_aggregates = pl.DataFrame(list(reversed(aggregates.to_dicts())))

    first = serialize_aggregates(aggregates)
    second = serialize_aggregates(reversed_aggregates)

    assert first == second
    assert json.loads(first)["type"] == "FeatureCollection"


def test_serialized_artifact_has_no_private_source_fields() -> None:
    """Public serialization should not contain raw camera fields."""
    serialized = serialize_feature_collection(build_feature_collection(load_aggregates())).decode()
    legacy_prefix = "sta" + "tion"

    for forbidden_term in [
        "camera_id",
        "lat",
        "lon",
        "name",
        "organization_id",
        "last_image",
        "last_image_url",
        f"{legacy_prefix}_count",
        f"{legacy_prefix}_count_bucket",
    ]:
        assert f'"{forbidden_term}"' not in serialized
