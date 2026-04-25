"""Workspace configuration tests."""

from __future__ import annotations

from pathlib import Path

import tomllib


def test_root_is_uv_workspace() -> None:
    """Root pyproject should coordinate packages without owning implementation."""
    root = Path(__file__).resolve().parents[1]
    config = tomllib.loads((root / "pyproject.toml").read_text())

    assert config["tool"]["uv"]["package"] is False
    assert config["tool"]["uv"]["workspace"]["members"] == ["packages/*"]
