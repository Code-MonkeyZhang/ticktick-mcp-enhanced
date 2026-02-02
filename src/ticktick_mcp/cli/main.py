"""
Main CLI entry point for TickTick.

Provides a command-line interface for managing TickTick tasks and projects.
Enhanced with flattened command structure and -h short option support.
"""

import typer
from typing import Optional

from . import __version__
from .commands.auth import app as auth_app
from .commands.tasks import app as tasks_app
from .commands.projects import app as projects_app
from .console import (
    console,
    print_success,
    print_info,
    create_task_table,
    create_project_table,
)

# Use context_settings to enable -h as help option
app = typer.Typer(
    help="TickTick CLI - Manage your tasks from the command line",
    no_args_is_help=True,
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"ticktick v{__version__}")
        raise typer.Exit()


# Register subcommands with -h support
auth_app.context_settings = {"help_option_names": ["-h", "--help"]}
tasks_app.context_settings = {"help_option_names": ["-h", "--help"]}
projects_app.context_settings = {"help_option_names": ["-h", "--help"]}

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


# Flattened top-level commands for common operations
@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def list(
    project: Optional[str] = typer.Option(
        None, "--project", "-p", help="Filter by project ID"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", help="Filter by priority (none/low/medium/high)"
    ),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search term"),
):
    """List all tasks across all projects."""
    from .context import CLIContext

    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    # Build filter function
    def task_filter(task):
        if priority:
            priority_map = {"none": 0, "low": 1, "medium": 3, "high": 5}
            if task.get("priority", 0) != priority_map.get(priority.lower(), 0):
                return False
        if search:
            search_lower = search.lower()
            title = task.get("title", "").lower()
            content = task.get("content", "").lower()
            if search_lower not in title and search_lower not in content:
                return False
        return True

    # Get tasks
    if project:
        project_data = client.get_project_with_data(project)
        if "error" in project_data:
            console.print(f"[red]Error fetching project: {project_data['error']}[/red]")
            raise typer.Exit(1)

        tasks = project_data.get("tasks", [])
        project_name = project_data.get("project", {}).get("name", project)
    else:
        projects = client.get_all_projects()
        if "error" in projects:
            console.print(f"[red]Error fetching projects: {projects['error']}[/red]")
            raise typer.Exit(1)

        tasks = []
        for proj in projects:
            proj_data = client.get_project_with_data(proj["id"])
            if "error" not in proj_data:
                tasks.extend(proj_data.get("tasks", []))
        project_name = "All Projects"

    # Apply filters
    filtered_tasks = [t for t in tasks if task_filter(t)]

    if not filtered_tasks:
        print_info("No tasks found matching the criteria")
        raise typer.Exit(0)

    # Display
    console.print(f"\n[bold]{project_name}[/bold] - {len(filtered_tasks)} tasks\n")
    table = create_task_table(filtered_tasks)
    console.print(table)


@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def today():
    """Show tasks due today."""
    from .context import CLIContext
    from datetime import datetime

    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    today_str = datetime.now().strftime("%Y-%m-%d")

    projects = client.get_all_projects()
    if "error" in projects:
        console.print(f"[red]Error fetching projects: {projects['error']}[/red]")
        raise typer.Exit(1)

    tasks = []
    for proj in projects:
        proj_data = client.get_project_with_data(proj["id"])
        if "error" not in proj_data:
            for task in proj_data.get("tasks", []):
                due_date = task.get("dueDate", "")
                if due_date and today_str in due_date:
                    tasks.append(task)

    if not tasks:
        print_info("No tasks due today")
        raise typer.Exit(0)

    console.print(f"\n[bold]Tasks Due Today[/bold] - {len(tasks)} tasks\n")
    table = create_task_table(tasks)
    console.print(table)


@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def overdue():
    """Show overdue tasks."""
    from .context import CLIContext
    from datetime import datetime, timezone

    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    now = datetime.now(timezone.utc)

    projects = client.get_all_projects()
    if "error" in projects:
        console.print(f"[red]Error fetching projects: {projects['error']}[/red]")
        raise typer.Exit(1)

    tasks = []
    for proj in projects:
        proj_data = client.get_project_with_data(proj["id"])
        if "error" not in proj_data:
            for task in proj_data.get("tasks", []):
                if task.get("status") == 0:  # Not completed
                    due_date = task.get("dueDate", "")
                    if due_date:
                        try:
                            dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                            if dt < now:
                                tasks.append(task)
                        except ValueError:
                            pass

    if not tasks:
        print_info("No overdue tasks")
        raise typer.Exit(0)

    console.print(f"\n[bold red]Overdue Tasks[/bold red] - {len(tasks)} tasks\n")
    table = create_task_table(tasks)
    console.print(table)


@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def projects():
    """List all projects."""
    from .context import CLIContext

    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    projects_list = client.get_all_projects()

    if "error" in projects_list:
        console.print(f"[red]Error fetching projects: {projects_list['error']}[/red]")
        raise typer.Exit(1)

    if not projects_list:
        print_info("No projects found")
        raise typer.Exit(0)

    console.print(f"\n[bold]Projects[/bold] - {len(projects_list)} projects\n")
    table = create_project_table(projects_list)
    console.print(table)


@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def examples():
    """Show usage examples."""
    console.print("\n[bold cyan]TickTick CLI Examples[/bold cyan]\n")

    console.print("[bold]Common Commands:[/bold]")
    console.print(
        "  [green]ticktick list[/green]              List all tasks\n"
        "  [green]ticktick today[/green]             Show tasks due today\n"
        "  [green]ticktick overdue[/green]           Show overdue tasks\n"
        "  [green]ticktick projects[/green]          List all projects\n"
    )

    console.print("\n[bold]Task Management:[/bold]")
    console.print(
        "  [green]ticktick tasks list[/green]        List tasks (with filters)\n"
        "  [green]ticktick tasks today[/green]       Show today's tasks\n"
        "  [green]ticktick tasks create[/green]      Create a new task\n"
        "  [green]ticktick tasks complete[/green]    Mark task as complete\n"
        "  [green]ticktick tasks delete[/green]      Delete a task\n"
    )

    console.print("\n[bold]Project Management:[/bold]")
    console.print(
        "  [green]ticktick projects list[/green]     List all projects\n"
        "  [green]ticktick projects create[/green]   Create a new project\n"
        "  [green]ticktick projects view[/green]     View project details\n"
        "  [green]ticktick projects delete[/green]   Delete a project\n"
    )

    console.print("\n[bold]Authentication:[/bold]")
    console.print(
        "  [green]ticktick auth login[/green]        Login to TickTick\n"
        "  [green]ticktick auth status[/green]       Check authentication status\n"
        "  [green]ticktick auth logout[/green]       Logout and clear credentials\n"
    )

    console.print("\n[bold]Filtering:[/bold]")
    console.print(
        "  [green]ticktick list --priority high[/green]     List high priority tasks\n"
        "  [green]ticktick list -s 'meeting'[/green]        Search for 'meeting'\n"
        "  [green]ticktick list -p <project-id>[/green]     List tasks in project\n"
    )

    console.print("\n[bold]Help:[/bold]")
    console.print(
        "  [green]ticktick -h[/green]               Show this help\n"
        "  [green]ticktick <command> -h[/green]     Show command-specific help\n"
    )

    console.print(
        "\n[dim]For more information, visit: https://github.com/moyueheng/ticktick-mcp-enhanced[/dim]\n"
    )


if __name__ == "__main__":
    app()
