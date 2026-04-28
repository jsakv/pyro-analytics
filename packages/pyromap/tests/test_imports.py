"""Import smoke tests for the Pyromap package."""

from __future__ import annotations

import importlib

import pyromap


def test_pyromap_package_imports() -> None:
    """The Pyromap package should expose a minimal public API."""
    assert pyromap.__version__ == "0.1.0"


def test_pyromap_modules_import_without_analytics() -> None:
    """Pyromap modules should import without depending on CLI wiring."""
    module_names = [
        "pyromap.config",
        "pyromap.cells",
        "pyromap.geojson",
        "pyromap.ingestion",
        "pyromap.publication",
        "pyromap.privacy",
        "pyromap.records",
        "pyromap.schemas",
        "pyromap.publishers.base",
        "pyromap.publishers.local",
        "pyromap.publishers.s3",
    ]

    for module_name in module_names:
        module = importlib.import_module(module_name)
        assert module.__name__ == module_name
