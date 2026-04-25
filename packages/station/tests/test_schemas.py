"""Tests for station source and public artifact schemas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from station import CellProperties, Result, Station

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


def load_api_cameras() -> list[dict[str, object]]:
    """Load synthetic API camera records."""
    payload = json.loads((FIXTURES_ROOT / "api-cameras.json").read_text())
    assert isinstance(payload, list)
    return payload


def test_station_schema_accepts_source_fixture_records() -> None:
    """Synthetic API records should normalize into typed source stations."""
    stations = [Station.model_validate(record) for record in load_api_cameras()]

    assert len(stations) == 3
    assert stations[0].id == 1001
    assert stations[0].lat == 43.6122
    assert stations[0].lon == 3.8849
    assert stations[0].poses[0].camera_id == 1001


def test_station_requires_coordinates() -> None:
    """Source station records need exact coordinates before aggregation."""
    record = load_api_cameras()[0].copy()
    del record["lat"]

    with pytest.raises(ValidationError, match="lat"):
        Station.model_validate(record)


def test_station_rejects_invalid_coordinate_ranges() -> None:
    """Invalid latitude and longitude values should fail schema validation."""
    record = load_api_cameras()[0]

    with pytest.raises(ValidationError, match="less than or equal to 90"):
        Station.model_validate(record | {"lat": 91.0})

    with pytest.raises(ValidationError, match="greater than or equal to -180"):
        Station.model_validate(record | {"lon": -181.0})


def test_cell_properties_accept_public_contract_fields() -> None:
    """Public cell properties should match the artifact contract."""
    properties = CellProperties.model_validate({
        "cell": "85396973fffffff",
        "station_count": 2,
        "station_count_bucket": "2-5",
    })

    assert properties.cell == "85396973fffffff"
    assert properties.station_count == 2
    assert properties.station_count_bucket == "2-5"


def test_cell_properties_reject_raw_coordinates() -> None:
    """Public feature properties must never expose exact station coordinates."""
    with pytest.raises(ValidationError, match="raw coordinate fields"):
        CellProperties.model_validate({
            "cell": "85396973fffffff",
            "station_count": 2,
            "station_count_bucket": "2-5",
            "lat": 43.6122,
        })


def test_cell_properties_reject_unknown_public_fields() -> None:
    """Only the explicit public property contract should validate."""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CellProperties.model_validate({
            "cell": "85396973fffffff",
            "station_count": 2,
            "station_count_bucket": "2-5",
            "name": "synthetic-montpellier-north",
        })


def test_result_schema_accepts_publish_metadata() -> None:
    """Publish results should contain counts and optional upload metadata."""
    result = Result(
        station_count=3,
        cell_count=2,
        bucket="pyronear-public-map-local",
        endpoint_url="http://localhost:9000",
        etag="synthetic-etag",
        published=True,
    )

    assert result.artifact_key == "station-cells.geojson"
    assert result.station_count == 3
    assert result.cell_count == 2
    assert result.published is True


def test_result_rejects_raw_coordinates() -> None:
    """Pipeline result metadata should stay safe for logs and CLI output."""
    with pytest.raises(ValidationError, match="raw coordinate fields"):
        Result.model_validate({"station_count": 3, "cell_count": 2, "lon": 3.8849})
