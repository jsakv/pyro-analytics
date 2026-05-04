"""Root CLI entrypoint and explicit workspace command composition."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import click
import typer
from pyromap.cli import COMMAND_KEY, DISPLAY_NAME
from pyromap.cli import create_app as create_pyromap_app

RESERVED_COMMAND_NAMES = frozenset({"help", "version"})


@dataclass(frozen=True, slots=True)
class WorkspaceCommandMount:
    """Describe one first-party workspace command group mounted by the root CLI."""

    command_key: str
    display_name: str
    create_app: Callable[[], typer.Typer]


class WorkspaceCommandConfigurationError(RuntimeError):
    """Raised when root CLI command composition is invalid."""

    @classmethod
    def reserved_command_key(cls, command_key: str) -> WorkspaceCommandConfigurationError:
        """Create an error for a reserved workspace command key."""
        return cls(f"Workspace command key '{command_key}' is reserved.")

    @classmethod
    def duplicate_command_key(cls, command_key: str) -> WorkspaceCommandConfigurationError:
        """Create an error for a duplicate workspace command key."""
        return cls(f"Duplicate workspace command key '{command_key}'.")


def create_app() -> typer.Typer:
    """Build the root Typer application."""
    app = typer.Typer(
        add_completion=False,
        help="Pyronear Analytics command line tools.",
        no_args_is_help=True,
    )
    _mount_workspace_commands(app)
    return app


def _workspace_commands() -> tuple[WorkspaceCommandMount, ...]:
    """Return the explicit list of first-party workspace command mounts."""
    return (
        WorkspaceCommandMount(
            command_key=COMMAND_KEY,
            display_name=DISPLAY_NAME,
            create_app=create_pyromap_app,
        ),
    )


def _mount_workspace_commands(app: typer.Typer) -> None:
    """Mount first-party workspace package apps onto the root CLI."""
    seen_command_keys: set[str] = set()
    for command_mount in _workspace_commands():
        if command_mount.command_key in RESERVED_COMMAND_NAMES:
            raise WorkspaceCommandConfigurationError.reserved_command_key(command_mount.command_key)
        if command_mount.command_key in seen_command_keys:
            raise WorkspaceCommandConfigurationError.duplicate_command_key(command_mount.command_key)
        seen_command_keys.add(command_mount.command_key)
        app.add_typer(
            command_mount.create_app(),
            name=command_mount.command_key,
            help=f"{command_mount.display_name} commands.",
        )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the root CLI dispatcher."""
    args = list(argv) if argv is not None else None
    try:
        result = create_app()(args=args, prog_name="pyro-analytics", standalone_mode=False)
        return result if isinstance(result, int) else 0
    except WorkspaceCommandConfigurationError as error:
        typer.echo(str(error), err=True)
        return 1
    except click.exceptions.Exit as error:
        return int(error.exit_code)
    except click.ClickException as error:
        error.show()
        return int(error.exit_code)
    except click.Abort:
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
