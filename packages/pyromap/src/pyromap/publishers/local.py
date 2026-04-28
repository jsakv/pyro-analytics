"""Local artifact publisher adapter."""

from __future__ import annotations

from pathlib import Path

from pyromap.publishers.base import GEOJSON_CONTENT_TYPE
from pyromap.schemas import Result


class LocalPublisher:
    """Write artifact bytes to a local staging path."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def publish(self, artifact: bytes, *, content_type: str = GEOJSON_CONTENT_TYPE) -> Result:
        """Write artifact bytes locally for staging and tests."""
        _ = content_type
        if not artifact:
            msg = "Artifact bytes must be non-empty."
            raise ValueError(msg)

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(artifact)
        return Result(artifact_key=str(self.path), published=True)
