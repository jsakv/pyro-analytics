"""Smoke tests for the root analytics CLI package."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from pyromap import Result
from typer.testing import CliRunner

import analytics
import analytics.cli
from analytics.cli import app

FIXTURES_ROOT = Path(__file__).parents[2] / "packages" / "pyromap" / "tests" / "fixtures"
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def plain_output(output: str) -> str:
    """Remove ANSI styling from Typer/Rich test output."""
    return ANSI_PATTERN.sub("", output)


def test_import_analytics_package() -> None:
    """The root CLI package should remain importable."""
    assert analytics.__version__ == "0.1.0"


def test_cli_help() -> None:
    """The root Typer app should expose help before domain commands exist."""
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Pyronear Analytics command line tools." in result.output


def test_camera_publish_help() -> None:
    """The camera publish command should expose source and local output options."""
    result = CliRunner().invoke(app, ["pyromap", "publish", "--help"])
    output = plain_output(result.output)

    assert result.exit_code == 0
    assert "--source" in output
    assert "--fixture-path" in output
    assert "--output" in output


def test_camera_publish_fixture_writes_local_artifact(tmp_path: Path) -> None:
    """Fixture source should publish locally without live services."""
    output_path = tmp_path / "camera-cells.geojson"

    result = CliRunner().invoke(
        app,
        [
            "pyromap",
            "publish",
            "--source",
            "fixture",
            "--fixture-path",
            str(FIXTURES_ROOT / "api-cameras.json"),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert "fetched=3" in result.output
    assert "published=2" in result.output
    assert "uploaded=1" in result.output
    payload = json.loads(output_path.read_text())
    assert payload["type"] == "FeatureCollection"


def test_pyromap_publish_delegates_to_pyromap_publish(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The CLI should delegate domain work to the PyroMap package."""
    calls: list[tuple[object, object]] = []

    def fake_publish(config: object, *, publisher: object | None = None) -> Result:
        calls.append((config, publisher))
        return Result(camera_count=7, cell_count=4, artifact_key="camera-cells.geojson", published=True)

    monkeypatch.setattr(analytics.cli, "publish_pyromap", fake_publish)

    result = CliRunner().invoke(
        app,
        [
            "pyromap",
            "publish",
            "--source",
            "fixture",
            "--fixture-path",
            str(FIXTURES_ROOT / "api-cameras.json"),
            "--output",
            str(tmp_path / "camera-cells.geojson"),
        ],
    )

    assert result.exit_code == 0
    assert calls
    assert "fetched=7 published=4 uploaded=1 artifact=camera-cells.geojson" in result.output


def test_camera_publish_fixture_requires_path() -> None:
    """Fixture source should fail clearly without a fixture path."""
    result = CliRunner().invoke(app, ["pyromap", "publish", "--source", "fixture"])
    output = plain_output(result.output)

    assert result.exit_code == 2
    assert "--fixture-path" in output


def test_camera_publish_maps_domain_failure_to_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Domain failures should become non-zero exits without private source output."""

    def fake_publish(config: object, *, publisher: object | None = None) -> Result:
        _ = config, publisher
        msg = "publish failed"
        raise ValueError(msg)

    monkeypatch.setattr(analytics.cli, "publish_pyromap", fake_publish)

    result = CliRunner().invoke(app, ["pyromap", "publish"])

    assert result.exit_code == 1
    assert "publish failed" in result.output
    assert "lat" not in result.output
    assert "lon" not in result.output
