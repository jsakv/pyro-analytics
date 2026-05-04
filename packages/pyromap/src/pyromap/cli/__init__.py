"""Typer app factory for the Pyromap workspace package."""

from __future__ import annotations

import typer

from pyromap.cli.commands.publish import publish

COMMAND_KEY = "pyromap"
DISPLAY_NAME = "Camera map publisher"


def create_app() -> typer.Typer:
    """Create the package-owned Typer application."""
    app = typer.Typer(
        help="Camera map publisher commands.",
        no_args_is_help=True,
    )
    app.callback()(_main)
    app.command("publish")(publish)
    return app


def _main() -> None:
    """Camera map publisher commands."""


__all__ = ["COMMAND_KEY", "DISPLAY_NAME", "create_app"]
