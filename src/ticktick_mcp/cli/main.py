"""
Main CLI entry point for TickTick.

Provides a command-line interface for managing TickTick tasks and projects.
Enhanced with flattened command structure and -h short option support.
"""

import typer
from typing import Optional
from rich.panel import Panel
from rich.table import Table
from rich import box

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


def print_help_with_examples():
    """Print custom help with formatted examples."""
    # Title
    console.print()
    console.print(
        "[bold]Usage:[/bold] [cyan]ticktick[/cyan] [OPTIONS] COMMAND [ARGS]..."
    )
    console.print()
    console.print("TickTick CLI - Manage your tasks from the command line")
    console.print()

    # Options section
    console.print("[bold blue]Options:[/bold blue]")
    options_table = Table(box=None, show_header=False, padding=(0, 2))
    options_table.add_column(style="cyan", width=18)
    options_table.add_column()
    options_table.add_row("-h, --help", "Show this message and exit.")
    options_table.add_row("-v, --version", "Show version and exit")
    console.print(options_table)
    console.print()

    # Commands section
    console.print("[bold green]Commands:[/bold green]")
    commands_table = Table(box=None, show_header=False, padding=(0, 2))
    commands_table.add_column(style="cyan", width=18)
    commands_table.add_column()
    commands_table.add_row("list", "List all tasks across all projects")
    commands_table.add_row("today", "Show tasks due today")
    commands_table.add_row("overdue", "Show overdue tasks")
    commands_table.add_row("projects", "List all projects")
    commands_table.add_row("auth", "Authentication commands")
    commands_table.add_row("tasks", "Task management commands")
    console.print(commands_table)
    console.print()

    # Examples section with styled panels
    console.print("[bold cyan]Examples:[/bold cyan]")
    console.print()

    # Quick Start
    quick_start = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    quick_start.add_column(style="green", width=36)
    quick_start.add_column(style="dim")
    quick_start.add_row("ticktick list", "List all tasks")
    quick_start.add_row("ticktick today", "Show today's tasks")
    quick_start.add_row("ticktick overdue", "Show overdue tasks")
    quick_start.add_row("ticktick projects", "List all projects")
    console.print(
        Panel(
            quick_start, title="[bold cyan]Quick Start[/bold cyan]", border_style="cyan"
        )
    )

    # Authentication
    auth_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    auth_table.add_column(style="green", width=36)
    auth_table.add_column(style="dim")
    auth_table.add_row("ticktick auth login", "Login to TickTick")
    auth_table.add_row("ticktick auth status", "Check auth status")
    auth_table.add_row("ticktick auth logout", "Logout")
    console.print(
        Panel(
            auth_table,
            title="[bold magenta]Authentication[/bold magenta]",
            border_style="magenta",
        )
    )

    # Task Management
    task_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    task_table.add_column(style="green", width=36)
    task_table.add_column(style="dim")
    task_table.add_row('ticktick tasks create "Task" -p <id>', "Create task")
    task_table.add_row("ticktick tasks complete <id> -p <id>", "Complete task")
    task_table.add_row("ticktick tasks delete <id> -p <id>", "Delete task")
    task_table.add_row("ticktick tasks view <id> -p <id>", "View task details")
    console.print(
        Panel(
            task_table,
            title="[bold yellow]Task Management[/bold yellow]",
            border_style="yellow",
        )
    )

    # Filtering
    filter_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    filter_table.add_column(style="green", width=36)
    filter_table.add_column(style="dim")
    filter_table.add_row("ticktick list --priority high", "High priority tasks")
    filter_table.add_row('ticktick list -s "keyword"', "Search tasks")
    filter_table.add_row("ticktick list -p <project-id>", "Tasks in project")
    console.print(
        Panel(
            filter_table,
            title="[bold blue]Filtering & Search[/bold blue]",
            border_style="blue",
        )
    )

    console.print()


# Main app - no_args_is_help disabled, we handle empty args in callback
app = typer.Typer(
    help="TickTick CLI - Manage your tasks from the command line",
    no_args_is_help=False,  # We handle this in callback to show custom help
    add_completion=False,
    rich_markup_mode="rich",
)


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"ticktick v{__version__}")
        raise typer.Exit()


def help_callback(value: bool):
    """Show custom help with examples and exit."""
    if value:
        print_help_with_examples()
        raise typer.Exit()


# Register subcommands
app.add_typer(auth_app, name="auth")
app.add_typer(tasks_app, name="tasks")
app.add_typer(projects_app, name="projects")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
    help: Optional[bool] = typer.Option(
        None,
        "--help",
        "-h",
        help="Show this message and exit.",
        callback=help_callback,
        is_eager=True,
    ),
):
    """TickTick CLI - Manage your tasks from the command line.

    If no command is specified, shows help with examples.
    """
    # If no subcommand was invoked, show custom help
    if ctx.resilient_parsing:
        return
    if ctx.invoked_subcommand is None:
        print_help_with_examples()
        raise typer.Exit()


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


if __name__ == "__main__":
    app()
