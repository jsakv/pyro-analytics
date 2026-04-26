"""Import smoke tests for the camera library package."""

from __future__ import annotations

import importlib

import cameras


def test_camera_package_imports() -> None:
    """The camera package should expose a minimal public API."""
    assert cameras.__version__ == "0.1.0"


def test_camera_scaffold_modules_import_without_analytics() -> None:
    """Scaffold modules should import without depending on CLI wiring."""
    module_names = [
        "cameras.config",
        "cameras.cells",
        "cameras.errors",
        "cameras.geojson",
        "cameras.pipeline",
        "cameras.privacy",
        "cameras.schemas",
        "cameras.serialization",
        "cameras.publishers.base",
        "cameras.publishers.local",
        "cameras.publishers.s3",
        "cameras.sources.api",
        "cameras.sources.base",
        "cameras.sources.fixture",
    ]

    for module_name in module_names:
        module = importlib.import_module(module_name)
        assert module.__name__ == module_name
