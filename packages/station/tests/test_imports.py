"""Import smoke tests for the station library package."""

from __future__ import annotations

import importlib

import station


def test_station_package_imports() -> None:
    """The station package should expose a minimal public API."""
    assert station.__version__ == "0.1.0"


def test_station_scaffold_modules_import_without_analytics() -> None:
    """Scaffold modules should import without depending on CLI wiring."""
    module_names = [
        "station.config",
        "station.cells",
        "station.errors",
        "station.geojson",
        "station.pipeline",
        "station.privacy",
        "station.schemas",
        "station.serialization",
        "station.publishers.base",
        "station.publishers.local",
        "station.publishers.s3",
        "station.sources.api",
        "station.sources.base",
        "station.sources.fixture",
    ]

    for module_name in module_names:
        module = importlib.import_module(module_name)
        assert module.__name__ == module_name
