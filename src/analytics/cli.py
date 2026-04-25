"""Typer entrypoint for Pyronear Analytics commands."""

from __future__ import annotations

import typer

app = typer.Typer(
    help="Pyronear Analytics command line tools.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Pyronear Analytics command line tools."""
