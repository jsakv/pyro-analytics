"""Tests for H3 cell indexing and aggregation."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
from pydantic import SecretStr
from pyromap import Camera, Config, LocationPolicy
from pyromap.cells import aggregate_cells, cameras_to_frame, index_cameras
from pyromap.records import load_fixture_records

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


def load_fixture_cameras() -> tuple[Camera, ...]:
    """Load typed synthetic cameras from the fixture source."""
    return load_fixture_records(FIXTURES_ROOT / "api-cameras.json", model=Camera)


def test_cameras_to_frame_contains_private_coordinates_before_indexing() -> None:
    """Camera records should become a Polars frame for vectorized transforms."""
    frame = cameras_to_frame(load_fixture_cameras())

    assert frame.columns == ["camera_id", "lat", "lon"]
    assert frame.height == 3
    assert frame.schema["lat"] == pl.Float64
    assert frame.schema["lon"] == pl.Float64


def test_index_cameras_uses_configured_resolution_and_drops_coordinates() -> None:
    """H3 indexing should use the requested resolution and remove raw coordinates."""
    frame = cameras_to_frame(load_fixture_cameras())

    indexed = index_cameras(frame, resolution=5)

    assert indexed.columns == ["camera_id", "cell"]
    assert "lat" not in indexed.columns
    assert "lon" not in indexed.columns
    assert indexed["cell"].to_list() == [
        "85396c5bfffffff",
        "85396c5bfffffff",
        "85396817fffffff",
    ]


def test_aggregate_cells_groups_fixture_cameras_deterministically() -> None:
    """Fixture cameras should aggregate into stable public cell properties."""
    aggregates = aggregate_cells(load_fixture_cameras(), Config())

    assert aggregates.to_dicts() == [
        {
            "cell": "85396803fffffff",
            "camera_count": 1,
            "camera_count_bucket": "1",
        },
        {
            "cell": "85396c5bfffffff",
            "camera_count": 2,
            "camera_count_bucket": "2-5",
        },
    ]


def test_aggregate_cells_uses_config_resolution() -> None:
    """Changing the configured H3 resolution should change grouping."""
    config = Config(location_policy=LocationPolicy(resolution=6))

    aggregates = aggregate_cells(load_fixture_cameras(), config)

    assert aggregates["camera_count"].to_list() == [1, 1, 1]
    assert aggregates["cell"].to_list() == [
        "863968147ffffff",
        "86396c587ffffff",
        "86396c597ffffff",
    ]


def test_aggregate_cells_can_preserve_exact_singleton_cells_when_shift_disabled() -> None:
    """The singleton shift can be disabled for fixture comparisons."""
    config = Config(singleton_cell_shift_enabled=False)

    aggregates = aggregate_cells(load_fixture_cameras(), config)

    assert aggregates.to_dicts() == [
        {
            "cell": "85396817fffffff",
            "camera_count": 1,
            "camera_count_bucket": "1",
        },
        {
            "cell": "85396c5bfffffff",
            "camera_count": 2,
            "camera_count_bucket": "2-5",
        },
    ]


def test_aggregate_cells_shifts_singletons_with_salted_determinism() -> None:
    """Singleton cells should move to a stable neighboring cell before publication."""
    config = Config(singleton_cell_shift_salt=SecretStr("alpha"))

    aggregates = aggregate_cells(load_fixture_cameras(), config)

    assert aggregates.to_dicts() == [
        {
            "cell": "853968bbfffffff",
            "camera_count": 1,
            "camera_count_bucket": "1",
        },
        {
            "cell": "85396c5bfffffff",
            "camera_count": 2,
            "camera_count_bucket": "2-5",
        },
    ]


def test_aggregate_cells_uses_salt_to_select_neighboring_singleton_cell() -> None:
    """Different salts should choose different public singleton neighbors."""
    pyromap = load_fixture_cameras()

    first = aggregate_cells(pyromap, Config(singleton_cell_shift_salt=SecretStr("alpha")))
    second = aggregate_cells(pyromap, Config(singleton_cell_shift_salt=SecretStr("beta")))

    assert first["cell"].to_list()[0] == "853968bbfffffff"
    assert second["cell"].to_list()[0] == "85396807fffffff"
    assert first["camera_count"].sum() == second["camera_count"].sum() == 3


def test_aggregate_cells_uses_approved_public_properties() -> None:
    """Aggregate output should be limited to configured public properties."""
    config = Config(location_policy=LocationPolicy(public_properties=("cell", "camera_count")))

    aggregates = aggregate_cells(load_fixture_cameras(), config)

    assert aggregates.columns == ["cell", "camera_count"]
    assert "lat" not in aggregates.columns
    assert "lon" not in aggregates.columns


def test_index_cameras_rejects_invalid_coordinates() -> None:
    """Invalid coordinates should fail before H3 indexing."""
    frame = pl.DataFrame(
        [{"camera_id": 1001, "lat": 91.0, "lon": 3.8849}],
        schema={"camera_id": pl.Int64, "lat": pl.Float64, "lon": pl.Float64},
    )

    with pytest.raises(ValueError, match="coordinates"):
        index_cameras(frame, resolution=5)
