"""Source protocol definitions."""

from __future__ import annotations

from typing import Protocol

from station.schemas import Station


class Source(Protocol):
    """Station source adapter contract."""

    def fetch(self) -> list[Station]:
        """Return normalized station source records."""
