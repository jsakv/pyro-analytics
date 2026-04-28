"""Tests for dlt ingestion boundaries."""

from __future__ import annotations

import pyromap.ingestion as ingestion
import pytest
from pyromap import Config
from pyromap.ingestion import run_cameras_ingestion


class FakePipeline:
    """Minimal dlt pipeline test double."""

    def __init__(self) -> None:
        self.run_calls: list[dict[str, object]] = []

    def run(self, data: object, **kwargs: object) -> object:
        """Record ingestion calls without transforming or publishing."""
        self.run_calls.append({"data": data, **kwargs})
        return {"loaded": True}


class FakeSource:
    """Minimal dlt source test double."""

    def __init__(self) -> None:
        self.selected_resources: tuple[str, ...] = ()

    def with_resources(self, *resources: str) -> FakeSource:
        """Record resource selection."""
        self.selected_resources = resources
        return self


def test_run_cameras_ingestion_runs_backend_source_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ingestion should run only the backend cameras dlt resource."""
    pipeline = FakePipeline()
    backend = FakeSource()

    monkeypatch.setattr("pyromap.ingestion.backend_source", lambda: backend)

    load_info = run_cameras_ingestion(Config(), pipeline=pipeline)

    assert load_info == {"loaded": True}
    assert backend.selected_resources == ("cameras",)
    assert pipeline.run_calls == [{"data": backend}]


def test_ingestion_module_does_not_expose_camera_schema() -> None:
    """Camera validation belongs to the PyroMap reader boundary."""
    assert "Camera" not in vars(ingestion)
