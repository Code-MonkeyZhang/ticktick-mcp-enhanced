"""
Console utilities for TickTick CLI.

Provides Rich console instance and formatting functions for consistent output.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Shared console instance
console = Console()


def print_success(message: str) -> None:
    """Print a success message with green checkmark."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message with red X."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message with yellow warning symbol."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message with blue info symbol."""
    console.print(f"[blue]ℹ[/blue] {message}")


def format_due_date(due_date: Optional[str]) -> str:
    """Format a due date string for display.

    Args:
        due_date: ISO 8601 date string or None

    Returns:
        Formatted date string or 'No due date' placeholder
    """
    if not due_date:
        return "No due date"

    try:
        # Parse ISO 8601 format
        dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return due_date[:16] if len(due_date) > 16 else due_date


def get_priority_label(priority: int) -> str:
    """Get priority label and color.

    Args:
        priority: 0 (none), 1 (low), 3 (medium), 5 (high)

    Returns:
        Rich-formatted priority label
    """
    labels = {
        5: "[red]High[/red]",
        3: "[yellow]Medium[/yellow]",
        1: "[blue]Low[/blue]",
        0: "[dim]None[/dim]",
    }
    return labels.get(priority, "[dim]None[/dim]")


def get_status_label(status: int) -> str:
    """Get status label.

    Args:
        status: 0 (normal), 1 (completed), 2 (archived)

    Returns:
        Rich-formatted status label
    """
    labels = {
        0: "[dim]○[/dim]",
        1: "[green]✓[/green]",
        2: "[dim]✓[/dim]",
    }
    return labels.get(status, "[dim]○[/dim]")


def create_task_table(
    tasks: List[Dict[str, Any]], title: Optional[str] = None
) -> Table:
    """Create a Rich table for displaying tasks.

    Args:
        tasks: List of task dictionaries
        title: Optional table title

    Returns:
        Rich Table instance
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold",
        show_lines=True,
    )

    table.add_column("Status", width=8, justify="center")
    table.add_column("Priority", width=10, justify="center")
    table.add_column("Title", min_width=30)
    table.add_column("Due Date", width=16)
    table.add_column("ID", width=24, style="dim")

    for task in tasks:
        status = task.get("status", 0)
        priority = task.get("priority", 0)
        title_text = task.get("title", "Untitled")
        due_date = format_due_date(task.get("dueDate"))
        task_id = task.get("id", "Unknown")

        table.add_row(
            get_status_label(status),
            get_priority_label(priority),
            title_text,
            due_date,
            task_id,
        )

    return table


def create_project_table(
    projects: List[Dict[str, Any]], title: Optional[str] = None
) -> Table:
    """Create a Rich table for displaying projects.

    Args:
        projects: List of project dictionaries
        title: Optional table title

    Returns:
        Rich Table instance
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold",
        show_lines=True,
    )

    table.add_column("Color", width=8, justify="center")
    table.add_column("Name", min_width=20)
    table.add_column("View Mode", width=12)
    table.add_column("ID", width=24, style="dim")

    for project in projects:
        color = project.get("color", "#F18181")
        name = project.get("name", "Unnamed")
        view_mode = project.get("viewMode", "list")
        project_id = project.get("id", "Unknown")

        # Show color as a colored square
        color_display = f"[{color}]■[/{color}]"

        table.add_row(
            color_display,
            name,
            view_mode.capitalize(),
            project_id,
        )

    return table


def print_task_detail(task: Dict[str, Any]) -> None:
    """Print detailed task information in a panel.

    Args:
        task: Task dictionary
    """
    title = task.get("title", "Untitled")
    content = task.get("content", "")
    priority = task.get("priority", 0)
    status = task.get("status", 0)
    due_date = format_due_date(task.get("dueDate"))
    task_id = task.get("id", "Unknown")

    status_text = "Completed" if status == 1 else "Active"

    text = Text()
    text.append(f"Title: ", style="bold")
    text.append(f"{title}\n")
    text.append(f"Status: ", style="bold")
    text.append(f"{status_text}\n")
    text.append(f"Priority: ", style="bold")
    text.append(f"{get_priority_label(priority)}\n")
    text.append(f"Due Date: ", style="bold")
    text.append(f"{due_date}\n")
    text.append(f"ID: ", style="bold")
    text.append(f"{task_id}\n")

    if content:
        text.append(f"\nContent:\n", style="bold")
        text.append(content)

    panel = Panel(text, title="Task Details", border_style="blue")
    console.print(panel)


def print_project_detail(project: Dict[str, Any], task_count: int = 0) -> None:
    """Print detailed project information in a panel.

    Args:
        project: Project dictionary
        task_count: Number of tasks in the project
    """
    name = project.get("name", "Unnamed")
    color = project.get("color", "#F18181")
    view_mode = project.get("viewMode", "list")
    project_id = project.get("id", "Unknown")

    text = Text()
    text.append(f"Name: ", style="bold")
    text.append(f"{name}\n")
    text.append(f"Color: ", style="bold")
    text.append(f"[{color}]{color}[/{color}]\n")
    text.append(f"View Mode: ", style="bold")
    text.append(f"{view_mode.capitalize()}\n")
    text.append(f"Tasks: ", style="bold")
    text.append(f"{task_count}\n")
    text.append(f"ID: ", style="bold")
    text.append(f"{project_id}")

    panel = Panel(text, title="Project Details", border_style="green")
    console.print(panel)
