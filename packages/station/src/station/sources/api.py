"""Pyronear API station source adapter."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import httpx
from pydantic import SecretStr, ValidationError

from station.config import Config
from station.schemas import Station


class ApiSource:
    """Fetch private station records from the Pyronear Alert API."""

    def __init__(self, config: Config, *, client: httpx.Client | None = None) -> None:
        self.api_url = _require_api_url(config)
        self.api_token = _require_api_token(config)
        self.client = client or httpx.Client(timeout=10.0)

    def fetch(self) -> list[Station]:
        """Fetch and normalize camera records into typed stations."""
        response = self._get_cameras()
        payload = self._decode_payload(response)

        if not isinstance(payload, list):
            msg = "pyro-api cameras response must be a JSON array."
            raise TypeError(msg)

        stations: list[Station] = []
        for index, record in enumerate(payload):
            if not isinstance(record, Mapping):
                msg = f"pyro-api cameras response record {index} must be an object."
                raise TypeError(msg)
            try:
                stations.append(Station.model_validate(record))
            except ValidationError as exc:
                msg = f"pyro-api cameras response record {index} is invalid."
                raise ValueError(msg) from exc
        return stations

    def _get_cameras(self) -> httpx.Response:
        try:
            response = self.client.get(_api_v1_url(self.api_url, "cameras/"), headers=self._headers())
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            msg = f"pyro-api cameras request failed with HTTP {exc.response.status_code}."
            raise ValueError(msg) from exc
        except httpx.RequestError as exc:
            msg = f"pyro-api cameras request failed: {exc.__class__.__name__}."
            raise ValueError(msg) from exc
        return response

    def _headers(self) -> dict[str, str]:
        token = self.api_token.get_secret_value()
        return {"Authorization": f"Bearer {token}"}

    def _decode_payload(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            msg = "pyro-api cameras response is not valid JSON."
            raise ValueError(msg) from exc


def _require_api_url(config: Config) -> str:
    if config.api_url is None:
        msg = "Missing required API setting: PYRONEAR_API_URL."
        raise ValueError(msg)
    return config.api_url.rstrip("/")


def _require_api_token(config: Config) -> SecretStr:
    if config.api_token is None:
        msg = "Missing required API setting: PYRONEAR_API_TOKEN."
        raise ValueError(msg)
    return config.api_token


def _api_v1_url(base_url: str, path: str) -> str:
    stripped_base = base_url.rstrip("/")
    if stripped_base.endswith("/api/v1"):
        return f"{stripped_base}/{path.lstrip('/')}"
    return f"{stripped_base}/api/v1/{path.lstrip('/')}"
