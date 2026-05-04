"""Smoke tests for the root analytics CLI package."""

from __future__ import annotations

import re

import pytest
import typer
from typer.testing import CliRunner

import analytics
import analytics.__main__ as analytics_main
from analytics.__main__ import WorkspaceCommandMount, create_app

ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def plain_output(output: str) -> str:
    """Remove ANSI styling from Typer/Rich test output."""
    return ANSI_PATTERN.sub("", output)


def test_import_analytics_package() -> None:
    """The root CLI package should remain importable."""
    assert analytics.__version__ == "0.1.0"


def test_cli_help_lists_pyromap_command_group() -> None:
    """Root help should expose the mounted Pyromap command group."""
    result = CliRunner().invoke(create_app(), ["--help"])

    assert result.exit_code == 0
    assert "Pyronear Analytics command line tools." in result.output
    assert "pyromap" in result.output


def test_pyromap_publish_help() -> None:
    """The Pyromap publish command should expose source and local output options."""
    result = CliRunner().invoke(create_app(), ["pyromap", "publish", "--help"])
    output = plain_output(result.output)

    assert result.exit_code == 0
    assert "--source" in output
    assert "--fixture-path" in output
    assert "--output" in output


def test_duplicate_workspace_command_keys_fail(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Duplicate first-party command keys should fail explicitly."""

    def fake_workspace_commands() -> tuple[WorkspaceCommandMount, ...]:
        return (
            WorkspaceCommandMount("pyromap", "Pyromap", typer.Typer),
            WorkspaceCommandMount("pyromap", "Duplicate Pyromap", typer.Typer),
        )

    monkeypatch.setattr(analytics_main, "_workspace_commands", fake_workspace_commands)

    result = analytics_main.main(["--help"])
    captured = capsys.readouterr()

    assert result == 1
    assert "Duplicate workspace command key 'pyromap'." in captured.err


def test_reserved_workspace_command_keys_fail(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Reserved first-party command keys should fail explicitly."""

    def fake_workspace_commands() -> tuple[WorkspaceCommandMount, ...]:
        return (WorkspaceCommandMount("help", "Help", typer.Typer),)

    monkeypatch.setattr(analytics_main, "_workspace_commands", fake_workspace_commands)

    result = analytics_main.main(["--help"])
    captured = capsys.readouterr()

    assert result == 1
    assert "Workspace command key 'help' is reserved." in captured.err
