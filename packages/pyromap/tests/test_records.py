"""Tests for typed fixture and dlt record readers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel
from pyromap import Camera
from pyromap.records import load_fixture_records, read_records

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


class MinimalRecord(BaseModel):
    """Small model used to verify generic record validation."""

    id: int


class FakeRelation:
    """Minimal dlt relation test double."""

    def df(self) -> FakeRelation:
        """Return a dataframe-like object."""
        return self

    def to_dict(self, *, orient: str) -> list[dict[str, object]]:
        """Return camera rows with dlt metadata."""
        assert orient == "records"
        return [
            {
                "id": 1001,
                "name": "synthetic-montpellier-north",
                "lat": 43.6122,
                "lon": 3.8849,
                "elevation": 640.0,
                "organization_id": 101,
                "angle_of_view": 110.0,
                "is_trustable": True,
                "created_at": "2026-01-10T09:00:00Z",
                "_dlt_load_id": "load",
            }
        ]


class FakeDataset:
    """Minimal dlt dataset test double."""

    def __getitem__(self, table_name: str) -> FakeRelation:
        assert table_name == "cameras"
        return FakeRelation()


class FakePipeline:
    """Pipeline test double with a readable dataset."""

    def dataset(self) -> FakeDataset:
        """Return a dataset relation map."""
        return FakeDataset()


def test_load_fixture_records_returns_requested_model_instances() -> None:
    """Fixture loading should return records typed by the requested model."""
    pyromap = load_fixture_records(FIXTURES_ROOT / "api-cameras.json", model=Camera)

    assert all(isinstance(camera, Camera) for camera in pyromap)


def test_load_fixture_records_works_with_any_pydantic_model(tmp_path: Path) -> None:
    """The reader should not be camera-specific."""
    fixture_path = tmp_path / "records.json"
    fixture_path.write_text(json.dumps([{"id": 1}, {"id": 2}]))

    records = load_fixture_records(fixture_path, model=MinimalRecord)

    assert records == (MinimalRecord(id=1), MinimalRecord(id=2))


def test_fixture_source_returns_typed_camera_records() -> None:
    """Valid fixture records should normalize into Camera objects."""
    pyromap = load_fixture_records(FIXTURES_ROOT / "api-cameras.json", model=Camera)

    assert len(pyromap) == 3
    assert pyromap[0].id == 1001
    assert pyromap[0].name == "synthetic-montpellier-north"
    assert pyromap[0].lat == 43.6122
    assert pyromap[0].lon == 3.8849


def test_fixture_source_missing_file_fails_actionably(tmp_path: Path) -> None:
    """Missing fixture files should fail before downstream processing."""
    with pytest.raises(ValueError, match="does not exist"):
        load_fixture_records(tmp_path / "missing.json", model=Camera)


def test_fixture_source_invalid_json_fails_actionably(tmp_path: Path) -> None:
    """Invalid JSON should produce a source-specific error."""
    fixture_path = tmp_path / "invalid.json"
    fixture_path.write_text("{")

    with pytest.raises(ValueError, match="not valid JSON"):
        load_fixture_records(fixture_path, model=Camera)


def test_fixture_source_requires_json_array(tmp_path: Path) -> None:
    """Fixture input should be an array of camera records."""
    fixture_path = tmp_path / "object.json"
    fixture_path.write_text(json.dumps({"id": 1001}))

    with pytest.raises(TypeError, match="JSON array"):
        load_fixture_records(fixture_path, model=Camera)


def test_fixture_source_requires_object_records(tmp_path: Path) -> None:
    """Each fixture item should be a camera-like object."""
    fixture_path = tmp_path / "scalar-record.json"
    fixture_path.write_text(json.dumps([1001]))

    with pytest.raises(TypeError, match="record 0"):
        load_fixture_records(fixture_path, model=Camera)


def test_fixture_source_invalid_record_fails_actionably(tmp_path: Path) -> None:
    """Camera schema errors should identify the fixture record index."""
    fixture_path = tmp_path / "invalid-record.json"
    fixture_path.write_text(json.dumps([{"id": 1001, "lat": 91.0}]))

    with pytest.raises(ValueError, match="record 0 is invalid"):
        load_fixture_records(fixture_path, model=Camera)


def test_read_records_ignores_dlt_metadata_fields() -> None:
    """dlt metadata should not leak into the requested model boundary."""
    cameras = read_records(FakePipeline(), table_name="cameras", model=Camera)

    assert len(cameras) == 1
    assert cameras[0].id == 1001
    assert cameras[0].lat == 43.6122
