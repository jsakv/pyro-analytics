"""Tests for the package-owned Pyromap CLI factory."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pyromap.cli.commands.publish as publish_command
import pytest
import typer
from pyromap import Result
from pyromap.cli import create_app
from typer.testing import CliRunner

FIXTURES_ROOT = Path(__file__).parent / "fixtures"
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def plain_output(output: str) -> str:
    """Remove ANSI styling from Typer/Rich test output."""
    return ANSI_PATTERN.sub("", output)


def test_create_app_returns_typer_app() -> None:
    """The package CLI factory should return a configured Typer app."""
    assert isinstance(create_app(), typer.Typer)


def test_publish_fixture_writes_local_artifact(tmp_path: Path) -> None:
    """Fixture source should publish locally without live services."""
    output_path = tmp_path / "camera-cells.geojson"

    result = CliRunner().invoke(
        create_app(),
        [
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


def test_publish_fixture_requires_path() -> None:
    """Fixture source should fail clearly without a fixture path."""
    result = CliRunner().invoke(create_app(), ["publish", "--source", "fixture"])
    output = plain_output(result.output)

    assert result.exit_code == 2
    assert "--fixture-path" in output


def test_publish_maps_domain_failure_to_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Domain failures should become non-zero exits without private source output."""

    def fake_publish(config: object, *, publisher: object | None = None) -> Result:
        _ = config, publisher
        msg = "publish failed"
        raise ValueError(msg)

    monkeypatch.setattr(publish_command, "publish_pyromap", fake_publish)

    result = CliRunner().invoke(create_app(), ["publish"])

    assert result.exit_code == 1
    assert "publish failed" in result.output
    assert "lat" not in result.output
    assert "lon" not in result.output
