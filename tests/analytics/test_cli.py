"""Smoke tests for the root analytics CLI package."""

from __future__ import annotations

from typer.testing import CliRunner

import analytics
from analytics.cli import app


def test_import_analytics_package() -> None:
    """The root CLI package should remain importable."""
    assert analytics.__version__ == "0.1.0"


def test_cli_help() -> None:
    """The root Typer app should expose help before domain commands exist."""
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Pyronear Analytics command line tools." in result.output
