"""Typer entrypoint for Pyronear Analytics commands."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
from pyromap import Config
from pyromap import publish as publish_pyromap
from pyromap.publishers import LocalPublisher

app = typer.Typer(
    help="Pyronear Analytics command line tools.",
    no_args_is_help=True,
)
pyromap_app = typer.Typer(
    help="Camera map publisher commands.",
    no_args_is_help=True,
)
app.add_typer(pyromap_app, name="pyromap")


class SourceChoice(StrEnum):
    """Pyromap source choices exposed by the CLI."""

    api = "api"
    fixture = "fixture"


@app.callback()
def main() -> None:
    """Pyronear Analytics command line tools."""


@pyromap_app.command("publish")
def pyromap_publish(
    source: Annotated[SourceChoice, typer.Option("--source", help="Camera source to publish from.")] = SourceChoice.api,
    fixture_path: Annotated[
        Path | None,
        typer.Option("--fixture-path", help="Fixture JSON file for fixture source."),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Write artifact locally instead of uploading to S3."),
    ] = None,
) -> None:
    """Publish the camera map artifact."""
    config = Config.from_env()
    if source is SourceChoice.fixture:
        if fixture_path is None:
            typer.echo("Missing required option for fixture source: --fixture-path.", err=True)
            raise typer.Exit(code=2)
        config = config.model_copy(update={"fixture_path": fixture_path})
    else:
        config = config.model_copy(update={"fixture_path": None})

    publisher = LocalPublisher(output) if output is not None else None
    try:
        result = publish_pyromap(config, publisher=publisher)
    except (TypeError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    uploaded_count = 1 if result.published else 0
    typer.echo(
        " ".join([
            f"fetched={result.camera_count}",
            f"published={result.cell_count}",
            f"uploaded={uploaded_count}",
            f"artifact={result.artifact_key}",
        ])
    )
