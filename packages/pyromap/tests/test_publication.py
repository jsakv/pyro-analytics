"""End-to-end tests for the camera publication flow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pyromap import Camera, Config, Result, publish
from pyromap.publishers import GEOJSON_CONTENT_TYPE
from pyromap.records import load_fixture_records

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


class FakePublisher:
    """Record artifact publication without network or filesystem writes."""

    def __init__(self, *, error: BaseException | None = None) -> None:
        self.error = error
        self.artifact: bytes | None = None
        self.content_type: str | None = None

    def publish(self, artifact: bytes, *, content_type: str = GEOJSON_CONTENT_TYPE) -> Result:
        """Record one artifact publish call."""
        if self.error is not None:
            raise self.error
        self.artifact = artifact
        self.content_type = content_type
        return Result(
            artifact_key="camera-cells.geojson",
            published=True,
            bucket="memory",
            endpoint_url="memory://camera",
            etag="fake-etag",
        )


def fixture_config() -> Config:
    """Build config that selects the synthetic fixture source."""
    return Config(fixture_path=FIXTURES_ROOT / "api-cameras.json")


def fixture_cameras() -> tuple[Camera, ...]:
    """Load typed fixture records."""
    return load_fixture_records(FIXTURES_ROOT / "api-cameras.json", model=Camera)


def test_publish_export_is_available() -> None:
    """The Pyromap package should expose the publication entrypoint."""
    assert callable(publish)


def test_publish_fixture_pipeline_with_fake_publisher() -> None:
    """Fixture input should produce and publish a validated GeoJSON artifact."""
    publisher = FakePublisher()

    result = publish(fixture_config(), publisher=publisher)

    assert result.published is True
    assert result.camera_count == 3
    assert result.cell_count == 2
    assert result.artifact_key == "camera-cells.geojson"
    assert publisher.content_type == "application/geo+json"
    assert publisher.artifact is not None
    payload = json.loads(publisher.artifact)
    assert payload["type"] == "FeatureCollection"
    assert [feature["properties"]["cell"] for feature in payload["features"]] == [
        "85396803fffffff",
        "85396c5bfffffff",
    ]


def test_publish_artifact_has_no_raw_coordinates() -> None:
    """Pipeline artifacts should not expose source coordinates or names."""
    publisher = FakePublisher()

    result = publish(fixture_config(), publisher=publisher)

    serialized_result = result.model_dump_json()
    assert "lat" not in serialized_result
    assert "lon" not in serialized_result
    assert publisher.artifact is not None
    serialized_artifact = publisher.artifact.decode()
    for forbidden_term in ["lat", "lon", "name", "organization_id", "last_image"]:
        assert f'"{forbidden_term}"' not in serialized_artifact


def test_publish_fixture_mode_bypasses_dlt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture input should not run dlt ingestion."""
    publisher = FakePublisher()

    def fail_ingestion(*args: object, **kwargs: object) -> object:
        msg = "dlt should not run"
        raise AssertionError(msg)

    monkeypatch.setattr("pyromap.publication.run_cameras_ingestion", fail_ingestion)

    result = publish(fixture_config(), publisher=publisher)

    assert result.camera_count == 3
    assert result.cell_count == 2


def test_publish_uses_backend_ingestion_without_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without fixture input, publication should ingest then read camera rows."""
    publisher = FakePublisher()
    calls: list[tuple[Config, Any]] = []
    pipeline = object()

    def fake_ingest(config: Config, *, pipeline: Any | None = None) -> object:
        calls.append((config, pipeline))
        return {"loaded": True}

    monkeypatch.setattr("pyromap.publication.build_pipeline", lambda config: pipeline)
    monkeypatch.setattr("pyromap.publication.run_cameras_ingestion", fake_ingest)
    monkeypatch.setattr(
        "pyromap.publication.read_records",
        lambda selected_pipeline, *, table_name, model: fixture_cameras(),
    )

    result = publish(Config(), publisher=publisher)

    assert calls == [(Config(), pipeline)]
    assert result.camera_count == 3
    assert result.cell_count == 2


def test_publish_fails_closed_on_invalid_fixture() -> None:
    """Source validation failures should stop before publishing."""
    publisher = FakePublisher()
    config = Config(fixture_path=FIXTURES_ROOT / "missing.json")

    with pytest.raises(ValueError, match="does not exist"):
        publish(config, publisher=publisher)

    assert publisher.artifact is None


def test_publish_fails_closed_on_invalid_transform_input(monkeypatch: pytest.MonkeyPatch) -> None:
    """Transform failures should stop before serialization and publishing."""
    invalid_camera = Camera.model_construct(
        id=1001,
        name="invalid-coordinate",
        lat=91.0,
        lon=3.8849,
        elevation=640.0,
        organization_id=101,
        angle_of_view=110.0,
        is_trustable=True,
        created_at="2026-01-10T09:00:00Z",
        poses=(),
        last_active_at=None,
        last_image=None,
        last_image_url=None,
    )
    publisher = FakePublisher()
    monkeypatch.setattr(
        "pyromap.publication.run_cameras_ingestion",
        lambda config, *, pipeline=None: object(),
    )
    monkeypatch.setattr(
        "pyromap.publication.read_records",
        lambda pipeline, *, table_name, model: (invalid_camera,),
    )

    with pytest.raises(ValueError, match="coordinates"):
        publish(Config(), publisher=publisher)

    assert publisher.artifact is None


def test_publish_fails_closed_on_serialization_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Serialization failures should stop before publishing."""
    publisher = FakePublisher()

    def fail_serialize(*args: object) -> bytes:
        msg = "serialization failed"
        raise ValueError(msg)

    monkeypatch.setattr("pyromap.publication.load_fixture_records", lambda path, *, model: fixture_cameras())
    monkeypatch.setattr("pyromap.publication.serialize_aggregates", fail_serialize)

    with pytest.raises(ValueError, match="serialization failed"):
        publish(fixture_config(), publisher=publisher)

    assert publisher.artifact is None


def test_publish_fails_closed_on_upload_error() -> None:
    """Publisher failures should propagate without producing a fake success."""
    publisher = FakePublisher(error=ValueError("upload failed"))

    with pytest.raises(ValueError, match="upload failed"):
        publish(fixture_config(), publisher=publisher)

    assert publisher.artifact is None
