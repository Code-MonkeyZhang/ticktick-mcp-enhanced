"""
Task commands for TickTick CLI.
"""

import typer
from typing import Optional, List

from ..context import CLIContext
from ..console import (
    print_success,
    print_error,
    print_info,
    print_warning,
    console,
    create_task_table,
    print_task_detail,
)


app = typer.Typer(help="Task management commands")


@app.command()
def list(
    project: Optional[str] = typer.Option(
        None, "--project", "-p", help="Filter by project ID"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", help="Filter by priority (none/low/medium/high)"
    ),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search term"),
):
    """List tasks with optional filters."""
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
            print_error(f"Error fetching project: {project_data['error']}")
            raise typer.Exit(1)

        tasks = project_data.get("tasks", [])
        project_name = project_data.get("project", {}).get("name", project)
    else:
        projects = client.get_all_projects()
        if "error" in projects:
            print_error(f"Error fetching projects: {projects['error']}")
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


@app.command()
def today():
    """Show tasks due today."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()
    from datetime import datetime

    today_str = datetime.now().strftime("%Y-%m-%d")

    projects = client.get_all_projects()
    if "error" in projects:
        print_error(f"Error fetching projects: {projects['error']}")
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


@app.command()
def overdue():
    """Show overdue tasks."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    projects = client.get_all_projects()
    if "error" in projects:
        print_error(f"Error fetching projects: {projects['error']}")
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


@app.command()
def create(
    title: str = typer.Argument(..., help="Task title"),
    project: str = typer.Option(..., "--project", "-p", help="Project ID"),
    content: Optional[str] = typer.Option(
        None, "--content", "-c", help="Task description"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", help="Priority (none/low/medium/high)"
    ),
    due: Optional[str] = typer.Option(
        None, "--due", "-d", help="Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)"
    ),
):
    """Create a new task."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    # Build task data
    task_data = {
        "title": title,
        "project_id": project,
    }

    if content:
        task_data["content"] = content

    if priority:
        priority_map = {"none": 0, "low": 1, "medium": 3, "high": 5}
        task_data["priority"] = priority_map.get(priority.lower(), 0)

    if due:
        # Parse due date
        from datetime import datetime

        try:
            if " " in due:
                dt = datetime.strptime(due, "%Y-%m-%d %H:%M")
            else:
                dt = datetime.strptime(due, "%Y-%m-%d")
            task_data["due_date"] = dt.isoformat()
        except ValueError:
            print_error("Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM")
            raise typer.Exit(1)

    result = client.create_task(**task_data)

    if "error" in result:
        print_error(f"Failed to create task: {result['error']}")
        raise typer.Exit(1)

    print_success(f"Task created: {result.get('title', title)}")
    print_info(f"ID: {result.get('id')}")


@app.command()
def complete(
    task_id: str = typer.Argument(..., help="Task ID"),
    project: str = typer.Option(..., "--project", "-p", help="Project ID"),
):
    """Mark a task as complete."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    result = client.complete_task(project, task_id)

    if "error" in result:
        print_error(f"Failed to complete task: {result['error']}")
        raise typer.Exit(1)

    print_success("Task marked as complete")


@app.command()
def delete(
    task_id: str = typer.Argument(..., help="Task ID"),
    project: str = typer.Option(..., "--project", "-p", help="Project ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a task."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm("Are you sure you want to delete this task?")
        if not confirm:
            print_info("Cancelled")
            raise typer.Exit(0)

    client = ctx.get_client()

    result = client.delete_task(project, task_id)

    if "error" in result:
        print_error(f"Failed to delete task: {result['error']}")
        raise typer.Exit(1)

    print_success("Task deleted")


@app.command()
def view(
    task_id: str = typer.Argument(..., help="Task ID"),
    project: str = typer.Option(..., "--project", "-p", help="Project ID"),
):
    """View task details."""
    ctx = CLIContext()

    if not ctx.require_auth():
        raise typer.Exit(1)

    client = ctx.get_client()

    task = client.get_task(project, task_id)

    if "error" in task:
        print_error(f"Failed to fetch task: {task['error']}")
        raise typer.Exit(1)

    print_task_detail(task)
