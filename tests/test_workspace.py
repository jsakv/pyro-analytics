"""Workspace configuration tests."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_root_is_uv_workspace() -> None:
    """Root pyproject should install the CLI and coordinate packages."""
    root = Path(__file__).resolve().parents[1]
    config = tomllib.loads((root / "pyproject.toml").read_text())

    assert config["project"]["scripts"]["pyro-analytics"] == "analytics.__main__:main"
    assert config["project"]["dependencies"] == ["sources", "pyromap", "typer"]
    assert config["tool"]["uv"]["workspace"]["members"] == ["packages/*"]
    assert config["tool"]["uv"]["sources"] == {
        "sources": {"workspace": True},
        "pyromap": {"workspace": True},
    }
    assert config["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == ["src/analytics"]
