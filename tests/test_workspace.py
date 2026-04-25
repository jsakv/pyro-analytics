"""Workspace configuration tests."""

from __future__ import annotations

from pathlib import Path

import tomllib


def test_root_is_uv_workspace() -> None:
    """Root pyproject should install the CLI and coordinate packages."""
    root = Path(__file__).resolve().parents[1]
    config = tomllib.loads((root / "pyproject.toml").read_text())

    assert config["project"]["scripts"]["analytics"] == "analytics.cli:app"
    assert config["tool"]["uv"]["workspace"]["members"] == ["packages/*"]
    assert config["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == ["src/analytics"]
