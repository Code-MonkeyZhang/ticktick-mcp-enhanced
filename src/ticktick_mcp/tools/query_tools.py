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
    PRIORITY_NAME_MAP,
)
from ..utils.timezone import to_ticktick_date_format, get_user_timezone_today
from ..utils.logging_utils import log_interaction
from .prompts import load_prompt

# logger = logging.getLogger(__name__)


def _resolve_completed_date_range(date_filter: str):
    """
    将快捷日期筛选映射为已完成任务 API 所需的 start_date / end_date。

    Args:
        date_filter: 快捷日期选项 — "today", "yesterday", "this_week", "this_month"

    Returns:
        (start_date, end_date) 元组，格式为 ISO 日期字符串（含时区偏移）。
    """
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    import os

    tz_name = os.getenv("TICKTICK_DISPLAY_TIMEZONE", "Local")
    if tz_name and tz_name != "Local":
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = None
    else:
        tz = None

    now = datetime.now(tz) if tz else datetime.now()
    today = now.date()

    if date_filter == "today":
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
    elif date_filter == "yesterday":
        yesterday = today - timedelta(days=1)
        start = datetime.combine(yesterday, datetime.min.time())
        end = datetime.combine(yesterday, datetime.max.time())
    elif date_filter == "this_week":
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        start = datetime.combine(monday, datetime.min.time())
        end = datetime.combine(sunday, datetime.max.time())
    elif date_filter == "this_month":
        first = today.replace(day=1)
        last_day = (first.replace(month=first.month % 12 + 1, day=1) - timedelta(days=1)).day if first.month < 12 else 31
        last = first.replace(day=last_day)
        start = datetime.combine(first, datetime.min.time())
        end = datetime.combine(last, datetime.max.time())
    else:
        return None, None

    if tz:
        start = start.replace(tzinfo=tz)
        end = end.replace(tzinfo=tz)
    else:
        start = start.replace(tzinfo=now.tzinfo)
        end = end.replace(tzinfo=now.tzinfo)

    fmt = "%Y-%m-%dT%H:%M:%S%z"
    return start.strftime(fmt), end.strftime(fmt)


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

    @mcp.tool(description=load_prompt("get_completed_tasks"))
    @log_interaction
    async def get_completed_tasks(
        project_id: Optional[str] = None,
        date_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        try:
            valid_date_filters = ["today", "yesterday", "this_week", "this_month", "custom"]
            if date_filter is not None and date_filter not in valid_date_filters:
                return f"Invalid date_filter. Must be one of: {', '.join(valid_date_filters)}"

            if date_filter == "custom" and (start_date is None or end_date is None):
                return "start_date and end_date are required when date_filter='custom'"

            ticktick = ensure_client()

            project_ids = None
            if project_id:
                project_ids = [project_id]

            if date_filter and date_filter != "custom":
                start_date, end_date = _resolve_completed_date_range(date_filter)

            if start_date:
                start_date = to_ticktick_date_format(start_date)
            if end_date:
                end_date = to_ticktick_date_format(end_date)

            result = ticktick.get_completed_tasks(
                project_ids=project_ids,
                start_date=start_date,
                end_date=end_date,
            )

            if isinstance(result, dict) and "error" in result:
                return f"Error fetching completed tasks: {result['error']}"

            tasks = result if isinstance(result, list) else []

            if not tasks:
                return "No completed tasks found."

            from ..utils.formatters import format_task

            output = f"Found {len(tasks)} completed tasks:\n\n"
            for i, task in enumerate(tasks, 1):
                output += f"Task {i}:\n" + format_task(task) + "\n"

            return output

        except Exception as e:
            return f"Error fetching completed tasks: {str(e)}"
