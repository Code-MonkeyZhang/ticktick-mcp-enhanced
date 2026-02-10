"""
Project commands for TickTick CLI.
"""

import typer
from typing import Optional

from ..context import CLIContext
from ..console import (
    print_success,
    print_error,
    print_info,
    console,
    create_project_table,
    print_project_detail,
)


app = typer.Typer(
    help="Project management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def list():
    """List all projects."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    projects = client.get_all_projects()

    if "error" in projects:
        print_error(f"Error fetching projects: {projects['error']}")
        raise typer.Exit(1)

    if not projects:
        print_info("No projects found")
        raise typer.Exit(0)

    console.print(f"\n[bold]Projects[/bold] - {len(projects)} projects\n")
    table = create_project_table(projects)
    console.print(table)


@app.command()
def create(
    name: str = typer.Argument(..., help="Project name"),
    color: Optional[str] = typer.Option(
        "#F18181", "--color", help="Project color (hex)"
    ),
    view_mode: Optional[str] = typer.Option(
        "list", "--view-mode", help="View mode (list/kanban/timeline)"
    ),
):
    """Create a new project."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    result = client.create_project(
        name=name,
        color=color,
        view_mode=view_mode,
    )

    if "error" in result:
        print_error(f"Failed to create project: {result['error']}")
        raise typer.Exit(1)

    print_success(f"Project created: {name}")
    print_info(f"ID: {result.get('id')}")


@app.command()
def view(
    project_id: str = typer.Argument(..., help="Project ID"),
):
    """View project details."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    project_data = client.get_project_with_data(project_id)

    if "error" in project_data:
        print_error(f"Error fetching project: {project_data['error']}")
        raise typer.Exit(1)

    project = project_data.get("project", {})
    tasks = project_data.get("tasks", [])

    print_project_detail(project, task_count=len(tasks))

    if tasks:
        from ..console import create_task_table

        console.print("\n[bold]Tasks[/bold]\n")
        table = create_task_table(tasks)
        console.print(table)


@app.command()
def delete(
    project_id: str = typer.Argument(..., help="Project ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a project."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm("Are you sure you want to delete this project?")
        if not confirm:
            print_info("Cancelled")
            raise typer.Exit(0)

    client = ctx.get_client()

    result = client.delete_project(project_id)

    if "error" in result:
        print_error(f"Failed to delete project: {result['error']}")
        raise typer.Exit(1)

    print_success("Project deleted")
