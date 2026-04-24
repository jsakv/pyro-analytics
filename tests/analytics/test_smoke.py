"""Smoke tests for generated package import behavior."""

from __future__ import annotations

from analytics import build_greeting


class TestPackageSmoke:
    """Verify package imports and basic greeting output."""

    def test_import_and_greeting(self) -> None:
        """Imported package should expose stable greeting behavior."""
        assert build_greeting("Pyronear") == "Hello, Pyronear."
