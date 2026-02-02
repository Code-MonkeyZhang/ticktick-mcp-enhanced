"""
Main CLI entry point for TickTick.

Provides a command-line interface for managing TickTick tasks and projects.
"""

import typer
from typing import Optional

from . import __version__
from .commands.auth import app as auth_app
from .commands.tasks import app as tasks_app
from .commands.projects import app as projects_app
from .console import console

app = typer.Typer(
    help="TickTick CLI - Manage your tasks from the command line",
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"ticktick v{__version__}")
        raise typer.Exit()


# Register subcommands
app.add_typer(auth_app, name="auth")
app.add_typer(tasks_app, name="tasks")
app.add_typer(projects_app, name="projects")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """TickTick CLI - Manage your tasks from the command line."""
    pass


if __name__ == "__main__":
    app()
