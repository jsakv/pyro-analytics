"""Contract tests for synthetic camera fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


def load_json_fixture(name: str) -> Any:
    """Load a JSON fixture from the camera fixture directory."""
    return json.loads((FIXTURES_ROOT / name).read_text())


def test_api_cameras_fixture_matches_camera_read_shape() -> None:
    """Source fixture should mimic the API boundary without credentials."""
    pyromap = load_json_fixture("api-cameras.json")

    assert isinstance(pyromap, list)
    assert pyromap
    for camera in pyromap:
        assert set(camera) == {
            "angle_of_view",
            "created_at",
            "elevation",
            "id",
            "is_trustable",
            "last_active_at",
            "last_image",
            "last_image_url",
            "lat",
            "lon",
            "name",
            "organization_id",
            "poses",
        }
        assert isinstance(camera["id"], int)
        assert -90 < camera["lat"] < 90
        assert -180 < camera["lon"] < 180
        assert "password" not in camera
        assert "token" not in camera


def test_public_geojson_fixture_contract() -> None:
    """Public fixture should expose only the approved cell properties."""
    artifact = load_json_fixture("camera-cells.geojson")

    assert artifact["type"] == "FeatureCollection"
    assert artifact["features"]
    for feature in artifact["features"]:
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Polygon"
        assert feature["geometry"]["coordinates"]
        assert set(feature["properties"]) == {"cell", "camera_count", "camera_count_bucket"}
        assert isinstance(feature["properties"]["cell"], str)
        assert isinstance(feature["properties"]["camera_count"], int)
        assert feature["properties"]["camera_count_bucket"] in {"1", "2-5", "6-10", "10+"}


def test_public_geojson_fixture_has_no_private_source_fields() -> None:
    """Public artifact must not leak source coordinates or camera fields."""
    serialized_artifact = (FIXTURES_ROOT / "camera-cells.geojson").read_text()
    legacy_prefix = "sta" + "tion"

    forbidden_terms = [
        "angle_of_view",
        "camera_id",
        "created_at",
        "elevation",
        "id",
        "is_trustable",
        "last_active_at",
        "last_image",
        "lat",
        "lon",
        "name",
        "organization_id",
        "poses",
        f"{legacy_prefix}_count",
        f"{legacy_prefix}_count_bucket",
    ]
    for term in forbidden_terms:
        assert f'"{term}"' not in serialized_artifact
