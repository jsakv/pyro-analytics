"""Tests for the Pyronear API station source adapter."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr
from station import Config, Station
from station.sources import ApiSource, Source

FIXTURES_ROOT = Path(__file__).parent / "fixtures"
AUTH_VALUE = "synthetic-token"


def load_api_cameras() -> list[dict[str, object]]:
    """Load synthetic API camera records."""
    payload = json.loads((FIXTURES_ROOT / "api-cameras.json").read_text())
    assert isinstance(payload, list)
    return payload


def make_client(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    """Create an httpx client backed by an in-memory transport."""
    return httpx.Client(transport=httpx.MockTransport(handler))


def make_secret() -> SecretStr:
    """Create a synthetic secret for mocked API tests."""
    return SecretStr(AUTH_VALUE)


def make_config() -> Config:
    """Create API source config without live credentials."""
    return Config(api_url="https://alertapi.pyronear.org", api_token=make_secret())


def test_api_source_matches_source_protocol() -> None:
    """ApiSource should satisfy the station source contract."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=load_api_cameras())

    source: Source = ApiSource(make_config(), client=make_client(handler))

    stations = source.fetch()

    assert all(isinstance(station, Station) for station in stations)


def test_api_source_fetches_cameras_with_bearer_token() -> None:
    """The API source should call the cameras endpoint with bearer auth."""
    seen_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return httpx.Response(200, json=load_api_cameras())

    source = ApiSource(make_config(), client=make_client(handler))

    stations = source.fetch()

    assert len(stations) == 3
    assert stations[0].id == 1001
    assert seen_requests[0].method == "GET"
    assert str(seen_requests[0].url) == "https://alertapi.pyronear.org/api/v1/cameras/"
    assert seen_requests[0].headers["Authorization"] == f"Bearer {AUTH_VALUE}"


def test_api_source_accepts_api_v1_base_url() -> None:
    """Configured API URLs may already include the version prefix."""
    seen_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, json=load_api_cameras())

    config = Config(api_url="https://alertapi.pyronear.org/api/v1", api_token=make_secret())
    source = ApiSource(config, client=make_client(handler))

    source.fetch()

    assert seen_urls == ["https://alertapi.pyronear.org/api/v1/cameras/"]


def test_api_source_requires_configured_url() -> None:
    """API URL should come from config before requests are attempted."""
    with pytest.raises(ValueError, match="PYRONEAR_API_URL"):
        ApiSource(Config(api_token=make_secret()), client=make_client(lambda request: httpx.Response(200)))


def test_api_source_requires_configured_token() -> None:
    """API token should come from config before requests are attempted."""
    with pytest.raises(ValueError, match="PYRONEAR_API_TOKEN"):
        ApiSource(
            Config(api_url="https://alertapi.pyronear.org"),
            client=make_client(lambda request: httpx.Response(200)),
        )


def test_api_source_auth_failure_is_actionable_without_token() -> None:
    """HTTP auth failures should not leak configured token values."""
    source = ApiSource(make_config(), client=make_client(lambda request: httpx.Response(401, text="invalid token")))

    with pytest.raises(ValueError, match="HTTP 401") as exc_info:
        source.fetch()

    assert AUTH_VALUE not in str(exc_info.value)


def test_api_source_http_error_is_actionable() -> None:
    """Non-auth HTTP failures should surface status code context."""
    source = ApiSource(make_config(), client=make_client(lambda request: httpx.Response(503, text="unavailable")))

    with pytest.raises(ValueError, match="HTTP 503"):
        source.fetch()


def test_api_source_request_error_is_actionable_without_token() -> None:
    """Transport failures should be wrapped without exposing credentials."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("x", request=request)

    source = ApiSource(make_config(), client=make_client(handler))

    with pytest.raises(ValueError, match="ConnectError") as exc_info:
        source.fetch()

    assert AUTH_VALUE not in str(exc_info.value)


def test_api_source_invalid_json_fails_actionably() -> None:
    """Invalid JSON responses should produce source-specific errors."""
    source = ApiSource(make_config(), client=make_client(lambda request: httpx.Response(200, text="{")))

    with pytest.raises(ValueError, match="not valid JSON"):
        source.fetch()


def test_api_source_requires_array_payload() -> None:
    """Camera fetch responses should be arrays of camera records."""
    source = ApiSource(make_config(), client=make_client(lambda request: httpx.Response(200, json={"id": 1001})))

    with pytest.raises(TypeError, match="JSON array"):
        source.fetch()


def test_api_source_requires_object_records() -> None:
    """Each camera record should be a JSON object."""
    source = ApiSource(make_config(), client=make_client(lambda request: httpx.Response(200, json=[1001])))

    with pytest.raises(TypeError, match="record 0"):
        source.fetch()


def test_api_source_invalid_record_fails_actionably() -> None:
    """Schema failures should identify the response record index."""
    source = ApiSource(
        make_config(),
        client=make_client(lambda request: httpx.Response(200, json=[{"id": 1001, "lat": 91.0}])),
    )

    with pytest.raises(ValueError, match="record 0 is invalid"):
        source.fetch()
