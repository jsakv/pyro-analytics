"""Fixture station source adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from station.schemas import Station


class FixtureSource:
    """Load synthetic station records from a local JSON fixture."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def fetch(self) -> list[Station]:
        """Read and normalize fixture records into typed stations."""
        payload = self._load_payload()
        if not isinstance(payload, list):
            msg = f"Fixture source {self.path} must contain a JSON array."
            raise TypeError(msg)

        stations: list[Station] = []
        for index, record in enumerate(payload):
            if not isinstance(record, dict):
                msg = f"Fixture source {self.path} record {index} must be an object."
                raise TypeError(msg)
            try:
                stations.append(Station.model_validate(record))
            except ValidationError as exc:
                msg = f"Fixture source {self.path} record {index} is invalid."
                raise ValueError(msg) from exc
        return stations

    def _load_payload(self) -> Any:
        try:
            return json.loads(self.path.read_text())
        except FileNotFoundError as exc:
            msg = f"Fixture source file does not exist: {self.path}."
            raise ValueError(msg) from exc
        except json.JSONDecodeError as exc:
            msg = f"Fixture source {self.path} is not valid JSON."
            raise ValueError(msg) from exc
