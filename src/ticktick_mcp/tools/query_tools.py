"""
Task query and filtering tools for TickTick MCP.

This module contains MCP tools for querying and filtering tasks
by various criteria such as due dates, priority, and search terms.
"""

# import logging
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

from ..client_manager import ensure_client
from ..utils.validators import (
    get_project_tasks_by_filter,
    is_task_due_today,
    is_task_overdue,
    is_task_due_in_days,
    task_matches_search,
    normalize_priority,
)
from ..utils.logging_utils import log_interaction
from .prompts import load_prompt

# logger = logging.getLogger(__name__)


def register_query_tools(mcp: FastMCP):
    """Register all query and filtering MCP tools."""

    @mcp.tool(description=load_prompt("query_tasks"))
    @log_interaction
    async def query_tasks(
        task_id: Optional[str] = None,
        project_id: Optional[str] = None,
        date_filter: Optional[str] = None,
        custom_days: Optional[int] = None,
        priority: Optional[str] = None,
        search_term: Optional[str] = None,
    ) -> str:
        try:
            """
            Validate Parameters
            """
            priority_value = None
            if priority is not None:
                priority_value = normalize_priority(priority)
                if priority_value is None:
                    valid_values = ", ".join(
                        [f'"{k}"' for k in ["none", "low", "medium", "high"]]
                    )
                    return (
                        f"Invalid priority '{priority}'. Must be one of: {valid_values}"
                    )

            valid_date_filters = [
                "today",
                "tomorrow",
                "overdue",
                "next_7_days",
                "custom",
            ]
            if date_filter is not None and date_filter not in valid_date_filters:
                return f"Invalid date_filter. Must be one of: {', '.join(valid_date_filters)}"

            if date_filter == "custom":
                if custom_days is None:
                    return "custom_days parameter is required when date_filter='custom'"
                if custom_days < 0:
                    return "custom_days must be a non-negative integer"

            if search_term is not None and not search_term.strip():
                return "Search term cannot be empty."

            ticktick = ensure_client()

            if task_id and project_id:
                task = ticktick.get_task(project_id, task_id)
                if "error" in task:
                    return f"Error fetching task: {task['error']}"

                from ..utils.formatters import format_task

                def single_task_filter(t: Dict[str, Any]) -> bool:
                    if date_filter == "today":
                        if not is_task_due_today(t):
                            return False
                    elif date_filter == "tomorrow":
                        if not is_task_due_in_days(t, 1):
                            return False
                    elif date_filter == "overdue":
                        if not is_task_overdue(t):
                            return False
                    elif date_filter == "next_7_days":
                        week_match = False
                        for day in range(7):
                            if is_task_due_in_days(t, day):
                                week_match = True
                                break
                        if not week_match:
                            return False
                    elif date_filter == "custom":
                        if not is_task_due_in_days(t, custom_days):
                            return False

                    if priority_value is not None:
                        if t.get("priority", 0) != priority_value:
                            return False

                    if search_term is not None:
                        if not task_matches_search(t, search_term):
                            return False

                    return True

                if not single_task_filter(task):
                    filter_parts = []
                    if date_filter:
                        filter_parts.append(f"date_filter={date_filter}")
                    if priority is not None:
                        filter_parts.append(f"priority='{priority}'")
                    if search_term:
                        filter_parts.append(f"search_term='{search_term}'")
                    filters_desc = ", ".join(filter_parts)
                    return f"Task {task_id} found but does not match the specified filters ({filters_desc})."

                return format_task(task)

            if project_id:
                project_data = ticktick.get_project_with_data(project_id)
                if "error" in project_data:
                    return f"Error fetching project data: {project_data['error']}"

                projects = [project_data.get("project", {})]
                all_tasks = project_data.get("tasks", [])
            else:
                projects = ticktick.get_all_projects()
                if "error" in projects:
                    return f"Error fetching projects: {projects['error']}"
                all_tasks = None

            def combined_filter(task: Dict[str, Any]) -> bool:
                if task_id is not None:
                    if task.get("id") != task_id:
                        return False

                if date_filter == "today":
                    if not is_task_due_today(task):
                        return False
                elif date_filter == "tomorrow":
                    if not is_task_due_in_days(task, 1):
                        return False
                elif date_filter == "overdue":
                    if not is_task_overdue(task):
                        return False
                elif date_filter == "next_7_days":
                    week_match = False
                    for day in range(7):
                        if is_task_due_in_days(task, day):
                            week_match = True
                            break
                    if not week_match:
                        return False
                elif date_filter == "custom":
                    if not is_task_due_in_days(task, custom_days):
                        return False

                if priority_value is not None:
                    if task.get("priority", 0) != priority_value:
                        return False

                if search_term is not None:
                    if not task_matches_search(task, search_term):
                        return False

                return True

            filter_descriptions = []
            if task_id is not None:
                filter_descriptions.append(f"task ID '{task_id}'")

            if date_filter == "today":
                filter_descriptions.append("due today")
            elif date_filter == "tomorrow":
                filter_descriptions.append("due tomorrow")
            elif date_filter == "overdue":
                filter_descriptions.append("overdue")
            elif date_filter == "next_7_days":
                filter_descriptions.append("due within next 7 days")
            elif date_filter == "custom":
                day_text = (
                    "today"
                    if custom_days == 0
                    else f"in {custom_days} day{'s' if custom_days != 1 else ''}"
                )
                filter_descriptions.append(f"due {day_text}")

            if priority is not None:
                filter_descriptions.append(f"priority {priority.capitalize()}")

            if search_term is not None:
                filter_descriptions.append(f"matching '{search_term}'")

            if project_id:
                project_name = (
                    projects[0].get("name", project_id) if projects else project_id
                )
                filter_descriptions.append(f"in project '{project_name}'")

            description = (
                " AND ".join(filter_descriptions)
                if filter_descriptions
                else "all tasks"
            )

            if project_id and all_tasks is not None:
                filtered_tasks = [task for task in all_tasks if combined_filter(task)]

                if not filtered_tasks:
                    return f"No tasks found ({description})."

                from ..utils.formatters import format_task

                result = f"Found {len(filtered_tasks)} tasks ({description}):\n\n"
                for i, task in enumerate(filtered_tasks, 1):
                    result += f"Task {i}:\n" + format_task(task) + "\n"

                return result
            else:
                return get_project_tasks_by_filter(
                    projects, combined_filter, description, ticktick
                )

        except Exception as e:
            # logger.error(f"Error in query_tasks: {e}")
            return f"Error querying tasks: {str(e)}"
