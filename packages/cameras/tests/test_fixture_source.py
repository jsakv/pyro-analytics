"""Tests for the fixture camera source adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cameras import Camera
from cameras.sources import FixtureSource, Source

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


def test_fixture_source_matches_source_protocol() -> None:
    """FixtureSource should satisfy the camera source contract."""
    source: Source = FixtureSource(FIXTURES_ROOT / "api-cameras.json")

    cameras = source.fetch()

    assert all(isinstance(camera, Camera) for camera in cameras)


def test_fixture_source_returns_typed_camera_records() -> None:
    """Valid fixture records should normalize into Camera objects."""
    source = FixtureSource(FIXTURES_ROOT / "api-cameras.json")

    cameras = source.fetch()

    assert len(cameras) == 3
    assert cameras[0].id == 1001
    assert cameras[0].name == "synthetic-montpellier-north"
    assert cameras[0].lat == 43.6122
    assert cameras[0].lon == 3.8849


def test_fixture_source_missing_file_fails_actionably(tmp_path: Path) -> None:
    """Missing fixture files should fail before downstream processing."""
    source = FixtureSource(tmp_path / "missing.json")

    with pytest.raises(ValueError, match="does not exist"):
        source.fetch()


def test_fixture_source_invalid_json_fails_actionably(tmp_path: Path) -> None:
    """Invalid JSON should produce a source-specific error."""
    fixture_path = tmp_path / "invalid.json"
    fixture_path.write_text("{")
    source = FixtureSource(fixture_path)

    with pytest.raises(ValueError, match="not valid JSON"):
        source.fetch()


def test_fixture_source_requires_json_array(tmp_path: Path) -> None:
    """Fixture input should be an array of camera records."""
    fixture_path = tmp_path / "object.json"
    fixture_path.write_text(json.dumps({"id": 1001}))
    source = FixtureSource(fixture_path)

    with pytest.raises(TypeError, match="JSON array"):
        source.fetch()


def test_fixture_source_requires_object_records(tmp_path: Path) -> None:
    """Each fixture item should be a camera-like object."""
    fixture_path = tmp_path / "scalar-record.json"
    fixture_path.write_text(json.dumps([1001]))
    source = FixtureSource(fixture_path)

    with pytest.raises(TypeError, match="record 0"):
        source.fetch()


def test_fixture_source_invalid_record_fails_actionably(tmp_path: Path) -> None:
    """Camera schema errors should identify the fixture record index."""
    fixture_path = tmp_path / "invalid-record.json"
    fixture_path.write_text(json.dumps([{"id": 1001, "lat": 91.0}]))
    source = FixtureSource(fixture_path)

    with pytest.raises(ValueError, match="record 0 is invalid"):
        source.fetch()
