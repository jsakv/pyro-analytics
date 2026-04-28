"""Publisher protocol definitions."""

from __future__ import annotations

from typing import Protocol

from pyromap.schemas import Result

GEOJSON_CONTENT_TYPE = "application/geo+json"


class Publisher(Protocol):
    """Artifact publisher contract."""

    def publish(self, artifact: bytes, *, content_type: str = GEOJSON_CONTENT_TYPE) -> Result:
        """Publish serialized artifact bytes."""
