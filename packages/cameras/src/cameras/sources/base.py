"""Source protocol definitions."""

from __future__ import annotations

from typing import Protocol

from cameras.schemas import Camera


class Source(Protocol):
    """Camera source adapter contract."""

    def fetch(self) -> list[Camera]:
        """Return normalized camera source records."""
