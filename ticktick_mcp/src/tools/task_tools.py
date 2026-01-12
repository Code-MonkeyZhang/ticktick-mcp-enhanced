"""
Task CRUD tools for TickTick MCP.

This module contains MCP tools for batch task operations.
All task operations support batch processing for improved efficiency.

Time handling:
- start_date/due_date must include timezone offset (e.g., 2025-12-16T16:00:00+0800)
- time_zone should be an IANA timezone name (e.g., "Asia/Shanghai")
- If due_date is omitted, task is treated as all-day
"""

import logging
from typing import List, Dict, Any, Union
from datetime import datetime
from mcp.server.fastmcp import FastMCP

from ..client_manager import ensure_client
from ..utils.formatters import format_task
from ..utils.timezone import normalize_iso_date, to_ticktick_date_format
from ..utils.logging_utils import log_interaction
from ..utils.validators import (
    validate_task_data,
    normalize_priority,
    validate_priority,
    normalize_batch_input,
    validate_required_fields,
    get_effective_timezone,
    format_batch_result,
)

logger = logging.getLogger(__name__)


def register_task_tools(mcp: FastMCP):
    """Register all task-related MCP tools."""

    @mcp.tool()
    @log_interaction
    async def create_tasks(tasks: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """
        Create one or more tasks in TickTick.

        Supports both single task and batch creation. For single task, you can pass
        a dictionary directly. For multiple tasks, pass a list of dictionaries.

        Args:
            tasks: Task dictionary or list of task dictionaries. Each task must contain:
                - title (required): Task Name
                - project_id (required): ID of the project for the task
                - content (optional): Task description
                - desc (optional): Description of checklist
                - start_date (optional): ISO datetime WITH timezone offset (e.g., 2025-12-16T08:00:00+0000)
                - due_date (optional): ISO datetime WITH timezone offset
                - time_zone (required): IANA timezone name (e.g. "Asia/Shanghai")
                - priority (optional): Priority level - "none", "low", "medium", or "high"
                - repeat_flag (optional): Recurring rules (e.g., "RRULE:FREQ=DAILY;INTERVAL=1")
                - items (optional): List of subtask dictionaries

        Examples:
            # Single task with Beijing timezone
            {
                "title": "Buy milk",
                "project_id": "1234ABC",
                "content": "2% organic",
                "due_date": "2025-12-16T16:00:00+08:00",
                "time_zone": "Asia/Shanghai",
                "priority": "medium"
            }

            # Multiple tasks (one timed, one all-day by omitting due_date)
            [
                {
                    "title": "Example A",
                    "project_id": "1234ABC",
                    "desc": "Timed task",
                    "due_date": "2025-07-19T10:00:00+0000",
                    "time_zone": "Asia/Shanghai",
                    "priority": "high"
                },
                {
                    "title": "Example B",
                    "project_id": "1234XYZ",
                    "content": "All-day task (no due_date means all-day)"
                }
            ]
        """
        task_list, single_task, error = normalize_batch_input(tasks, "Task")
        if error:
            return error

        validation_errors = []
        for i, task_data in enumerate(task_list):
            if not isinstance(task_data, dict):
                validation_errors.append(f"Task {i + 1}: Must be a dictionary")
                continue
            err = validate_task_data(task_data, i)
            if err:
                validation_errors.append(err)

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        created_tasks = []
        failed_tasks = []

        try:
            ticktick = ensure_client()
            for i, task_data in enumerate(task_list):
                try:
                    title = task_data["title"]
                    result = ticktick.create_task(
                        title=title,
                        project_id=task_data["project_id"],
                        content=task_data.get("content"),
                        desc=task_data.get("desc"),
                        start_date=to_ticktick_date_format(task_data.get("start_date")),
                        due_date=to_ticktick_date_format(task_data.get("due_date")),
                        time_zone=get_effective_timezone(task_data.get("time_zone")),
                        priority=normalize_priority(task_data.get("priority", 0)) or 0,
                        repeat_flag=task_data.get("repeat_flag"),
                        items=task_data.get("items"),
                    )

                    if "error" in result:
                        failed_tasks.append(
                            f"Task {i + 1} ('{title}'): {result['error']}"
                        )
                    else:
                        created_tasks.append((i + 1, title, result))
                except Exception as e:
                    failed_tasks.append(
                        f"Task {i + 1} ('{task_data.get('title', 'Unknown')}'): {str(e)}"
                    )

            return format_batch_result(
                created_tasks,
                failed_tasks,
                "created",
                "task",
                single_task,
                single_success_formatter=lambda item: f"Task created successfully:\n\n{format_task(item[2])}",
                batch_item_formatter=lambda item: f"{item[0]}. {item[1]} (ID: {item[2].get('id', 'Unknown')})",
            )

        except Exception as e:
            logger.error(f"Error in create_tasks: {e}")
            return f"Error during task creation: {str(e)}"

    @mcp.tool()
    @log_interaction
    async def update_tasks(tasks: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """
        Update one or more existing tasks in TickTick.

        Supports both single task and batch updates. For single task, you can pass
        a dictionary directly. For multiple tasks, pass a list of dictionaries.

        Args:
            tasks: Task dictionary or list of task dictionaries. Each task must contain:
                - task_id (required): ID of the task to update
                - project_id (required): ID of the project the task belongs to
                - title (optional): task title
                - content (optional): task description/content
                - desc (optional): description of checklist
                - start_date (optional): ISO datetime WITH timezone offset
                - due_date (optional): ISO datetime WITH timezone offset; omit to make an all-day task
                - time_zone (optional): IANA timezone name (e.g., "Asia/Shanghai", "America/New_York")
                - priority (optional): priority level - "none", "low", "medium", or "high"
                - repeat_flag (optional): Recurring rules
                - items (optional): List of subtask dictionaries

        Examples:
            # Single task update (set due date with timezone)
            {
                "task_id": "abc123",
                "project_id": "xyz789",
                "title": "Updated title",
                "due_date": "2025-12-31T15:00:00+08:00",
                "time_zone": "Asia/Shanghai",
                "priority": "high"
            }

        """
        task_list, single_task, error = normalize_batch_input(tasks, "Task")
        if error:
            return error

        validation_errors = []
        for i, task_data in enumerate(task_list):
            field_errors = validate_required_fields(
                task_data, ["task_id", "project_id"], i
            )
            validation_errors.extend(field_errors)
            if field_errors:
                continue

            priority = task_data.get("priority")
            if priority is not None:
                priority_error = validate_priority(priority, i)
                if priority_error:
                    validation_errors.append(priority_error)

            for date_field in ["start_date", "due_date"]:
                date_str = task_data.get(date_field)
                if date_str:
                    try:
                        normalized_date = normalize_iso_date(date_str)
                        dt = datetime.fromisoformat(normalized_date)
                        if dt.tzinfo is None:
                            validation_errors.append(
                                f"Task {i + 1}: {date_field} must include timezone offset (e.g., +08:00 or +0000)"
                            )
                    except ValueError:
                        validation_errors.append(
                            f"Task {i + 1}: Invalid {date_field} format '{date_str}'"
                        )

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        updated_tasks = []
        failed_tasks = []

        try:
            ticktick = ensure_client()
            for i, task_data in enumerate(task_list):
                try:
                    task_id = task_data["task_id"]
                    start_date = to_ticktick_date_format(task_data.get("start_date"))
                    due_date = to_ticktick_date_format(task_data.get("due_date"))

                    time_zone = task_data.get("time_zone")
                    if not time_zone and (start_date or due_date):
                        time_zone = get_effective_timezone()

                    result = ticktick.update_task(
                        task_id=task_id,
                        project_id=task_data["project_id"],
                        title=task_data.get("title"),
                        content=task_data.get("content"),
                        desc=task_data.get("desc"),
                        start_date=start_date,
                        due_date=due_date,
                        time_zone=time_zone,
                        priority=normalize_priority(task_data.get("priority")),
                        repeat_flag=task_data.get("repeat_flag"),
                        items=task_data.get("items"),
                    )

                    if "error" in result:
                        failed_tasks.append(
                            f"Task {i + 1} (ID: {task_id}): {result['error']}"
                        )
                    else:
                        updated_tasks.append((i + 1, task_id, result))
                except Exception as e:
                    failed_tasks.append(
                        f"Task {i + 1} (ID: {task_data.get('task_id', 'Unknown')}): {str(e)}"
                    )

            return format_batch_result(
                updated_tasks,
                failed_tasks,
                "updated",
                "task",
                single_task,
                single_success_formatter=lambda item: f"Task updated successfully:\n\n{format_task(item[2])}",
                batch_item_formatter=lambda item: f"{item[0]}. {item[2].get('title', 'Unknown')} (ID: {item[1]})",
            )

        except Exception as e:
            logger.error(f"Error in update_tasks: {e}")
            return f"Error during task update: {str(e)}"

    @mcp.tool()
    @log_interaction
    async def complete_tasks(tasks: Union[Dict[str, str], List[Dict[str, str]]]) -> str:
        """
        Mark one or more tasks as complete.

        Supports both single task and batch completion. For single task, you can pass
        a dictionary directly. For multiple tasks, pass a list of dictionaries.

        Args:
            tasks: Task dictionary or list of task dictionaries. Each task must contain:
                - project_id (required): ID of the project
                - task_id (required): ID of the task

        Examples:
            # Single task
            {"project_id": "xyz789", "task_id": "abc123"}

            # Multiple tasks
            [
                {"project_id": "xyz789", "task_id": "abc123"},
                {"project_id": "xyz789", "task_id": "def456"},
                {"project_id": "abc123", "task_id": "ghi789"}
            ]
        """
        task_list, single_task, error = normalize_batch_input(tasks, "Task")
        if error:
            return error

        validation_errors = []
        for i, task_data in enumerate(task_list):
            validation_errors.extend(
                validate_required_fields(task_data, ["task_id", "project_id"], i)
            )

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        completed_tasks = []
        failed_tasks = []

        try:
            ticktick = ensure_client()
            for i, task_data in enumerate(task_list):
                try:
                    task_id = task_data["task_id"]
                    result = ticktick.complete_task(task_data["project_id"], task_id)

                    if "error" in result:
                        failed_tasks.append(
                            f"Task {i + 1} (ID: {task_id}): {result['error']}"
                        )
                    else:
                        completed_tasks.append((i + 1, task_id))
                except Exception as e:
                    failed_tasks.append(
                        f"Task {i + 1} (ID: {task_data.get('task_id', 'Unknown')}): {str(e)}"
                    )

            return format_batch_result(
                completed_tasks,
                failed_tasks,
                "completed",
                "task",
                single_task,
                single_success_formatter=lambda item: f"Task {item[1]} marked as complete.",
                batch_item_formatter=lambda item: f"{item[0]}. Task ID: {item[1]}",
            )

        except Exception as e:
            logger.error(f"Error in complete_tasks: {e}")
            return f"Error during task completion: {str(e)}"

    @mcp.tool()
    @log_interaction
    async def delete_tasks(tasks: Union[Dict[str, str], List[Dict[str, str]]]) -> str:
        """
        Delete one or more tasks.

        Supports both single task and batch deletion. For single task, you can pass
        a dictionary directly. For multiple tasks, pass a list of dictionaries.

        Args:
            tasks: Task dictionary or list of task dictionaries. Each task must contain:
                - project_id (required): ID of the project
                - task_id (required): ID of the task

        Examples:
            # Single task
            {"project_id": "xyz789", "task_id": "abc123"}

            # Multiple tasks
            [
                {"project_id": "xyz789", "task_id": "abc123"},
                {"project_id": "xyz789", "task_id": "def456"},
                {"project_id": "abc123", "task_id": "ghi789"}
            ]
        """
        task_list, single_task, error = normalize_batch_input(tasks, "Task")
        if error:
            return error

        validation_errors = []
        for i, task_data in enumerate(task_list):
            validation_errors.extend(
                validate_required_fields(task_data, ["task_id", "project_id"], i)
            )

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        deleted_tasks = []
        failed_tasks = []

        try:
            ticktick = ensure_client()
            for i, task_data in enumerate(task_list):
                try:
                    task_id = task_data["task_id"]
                    result = ticktick.delete_task(task_data["project_id"], task_id)

                    if "error" in result:
                        failed_tasks.append(
                            f"Task {i + 1} (ID: {task_id}): {result['error']}"
                        )
                    else:
                        deleted_tasks.append((i + 1, task_id))
                except Exception as e:
                    failed_tasks.append(
                        f"Task {i + 1} (ID: {task_data.get('task_id', 'Unknown')}): {str(e)}"
                    )

            return format_batch_result(
                deleted_tasks,
                failed_tasks,
                "deleted",
                "task",
                single_task,
                single_success_formatter=lambda item: f"Task {item[1]} deleted successfully.",
                batch_item_formatter=lambda item: f"{item[0]}. Task ID: {item[1]}",
            )

        except Exception as e:
            logger.error(f"Error in delete_tasks: {e}")
            return f"Error during task deletion: {str(e)}"

    @mcp.tool()
    @log_interaction
    async def create_subtasks(
        subtasks: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> str:
        """
        Create one or more subtasks for parent tasks. For single subtask, you can pass
        a dictionary directly. For multiple subtasks, pass a list of dictionaries.

        Args:
            subtasks: Subtask dictionary or list of subtask dictionaries. Each subtask must contain:
                - subtask_title (required): Title of the subtask
                - parent_task_id (required): ID of the parent task
                - project_id (required): ID of the project (must be same for both parent and subtask)
                - content (optional): Content/description for the subtask
                - priority (optional): Priority level - "none", "low", "medium", or "high" (case-insensitive)

        Examples:
            # Single subtask
            {"subtask_title": "Subtask 1", "parent_task_id": "abc123", "project_id": "xyz789"}

            # Multiple subtasks
            [
                {"subtask_title": "Subtask 1", "parent_task_id": "abc123", "project_id": "xyz789", "priority": "medium"},
                {"subtask_title": "Subtask 2", "parent_task_id": "abc123", "project_id": "xyz789", "content": "Details"}
            ]
        """
        subtask_list, single_subtask, error = normalize_batch_input(subtasks, "Subtask")
        if error:
            return error

        validation_errors = []
        for i, subtask_data in enumerate(subtask_list):
            field_errors = validate_required_fields(
                subtask_data,
                ["subtask_title", "parent_task_id", "project_id"],
                i,
                "Subtask",
            )
            validation_errors.extend(field_errors)
            if field_errors:
                continue

            priority = subtask_data.get("priority")
            if priority is not None:
                priority_error = validate_priority(priority, i)
                if priority_error:
                    validation_errors.append(priority_error.replace("Task", "Subtask"))

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        created_subtasks = []
        failed_subtasks = []

        try:
            ticktick = ensure_client()
            for i, subtask_data in enumerate(subtask_list):
                try:
                    subtask_title = subtask_data["subtask_title"]
                    result = ticktick.create_subtask(
                        subtask_title=subtask_title,
                        parent_task_id=subtask_data["parent_task_id"],
                        project_id=subtask_data["project_id"],
                        content=subtask_data.get("content"),
                        priority=normalize_priority(subtask_data.get("priority", 0))
                        or 0,
                    )

                    if "error" in result:
                        failed_subtasks.append(
                            f"Subtask {i + 1} ('{subtask_title}'): {result['error']}"
                        )
                    else:
                        created_subtasks.append((i + 1, subtask_title, result))
                except Exception as e:
                    failed_subtasks.append(
                        f"Subtask {i + 1} ('{subtask_data.get('subtask_title', 'Unknown')}'): {str(e)}"
                    )

            return format_batch_result(
                created_subtasks,
                failed_subtasks,
                "created",
                "subtask",
                single_subtask,
                single_success_formatter=lambda item: f"Subtask created successfully:\n\n{format_task(item[2])}",
                batch_item_formatter=lambda item: f"{item[0]}. {item[1]} (ID: {item[2].get('id', 'Unknown')})",
            )

        except Exception as e:
            logger.error(f"Error in create_subtasks: {e}")
            return f"Error during subtask creation: {str(e)}"
