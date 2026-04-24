"""Behavior-focused tests for greeting behavior."""

from __future__ import annotations

import pytest

from analytics.core import build_greeting


class TestBuildGreeting:
    """Verify deterministic greeting behavior for the core domain helper."""

    def test_supports_excitement(self) -> None:
        """Greeting should include exclamation when requested."""
        assert build_greeting("Pyronear", include_excitement=True) == "Hello, Pyronear!"

    def test_rejects_blank_name(self) -> None:
        """Blank names should raise a specific actionable error."""
        with pytest.raises(ValueError, match="non-empty"):
            build_greeting("   ")
