"""Tests for committed demo camera map examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cameras import Config
from cameras.cells import aggregate_cells
from cameras.schemas import Camera

ROOT = Path(__file__).resolve().parents[2]
DEMO_SOURCE = ROOT / "examples" / "cameras" / "demo-api-cameras.json"
DEMO_GEOJSON = ROOT / "examples" / "cameras" / "demo-camera-cells.geojson"


def load_json(path: Path) -> Any:
    """Load a committed demo JSON artifact."""
    return json.loads(path.read_text())


def test_demo_source_contains_multi_camera_cells_up_to_four() -> None:
    """Demo source data should exercise map density buckets."""
    cameras = [Camera.model_validate(record) for record in load_json(DEMO_SOURCE)]

    aggregates = aggregate_cells(cameras, Config())
    counts = sorted(aggregates["camera_count"].to_list(), reverse=True)

    assert len(cameras) == 66
    assert counts[:3] == [4, 3, 2]
    assert max(counts) == 4


def test_demo_geojson_matches_demo_source_density() -> None:
    """Committed demo GeoJSON should mirror the generated source aggregates."""
    source_cameras = [Camera.model_validate(record) for record in load_json(DEMO_SOURCE)]
    source_counts_by_cell = {
        row["cell"]: row["camera_count"] for row in aggregate_cells(source_cameras, Config()).iter_rows(named=True)
    }

    artifact = load_json(DEMO_GEOJSON)
    feature_counts_by_cell = {
        feature["properties"]["cell"]: feature["properties"]["camera_count"] for feature in artifact["features"]
    }

    assert artifact["type"] == "FeatureCollection"
    assert feature_counts_by_cell == source_counts_by_cell
    assert sorted(feature_counts_by_cell.values(), reverse=True)[:3] == [4, 3, 2]
