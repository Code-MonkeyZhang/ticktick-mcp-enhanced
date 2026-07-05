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
from .prompts import load_prompt
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

    @mcp.tool(description=load_prompt("create_tasks"))
    @log_interaction
    async def create_tasks(tasks: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
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
                        reminders=task_data.get("reminders"),
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
            # logger.error(f"Error in create_tasks: {e}")
            return f"Error during task creation: {str(e)}"

    @mcp.tool(description=load_prompt("update_tasks"))
    @log_interaction
    async def update_tasks(tasks: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
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
                        reminders=task_data.get("reminders"),
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
            # logger.error(f"Error in update_tasks: {e}")
            return f"Error during task update: {str(e)}"

    @mcp.tool(description=load_prompt("complete_tasks"))
    @log_interaction
    async def complete_tasks(tasks: Union[Dict[str, str], List[Dict[str, str]]]) -> str:
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
            # logger.error(f"Error in complete_tasks: {e}")
            return f"Error during task completion: {str(e)}"

    @mcp.tool(description=load_prompt("delete_tasks"))
    @log_interaction
    async def delete_tasks(tasks: Union[Dict[str, str], List[Dict[str, str]]]) -> str:
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
            # logger.error(f"Error in delete_tasks: {e}")
            return f"Error during task deletion: {str(e)}"

    @mcp.tool(description=load_prompt("create_subtasks"))
    @log_interaction
    async def create_subtasks(
        subtasks: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> str:
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
            # logger.error(f"Error in create_subtasks: {e}")
            return f"Error during subtask creation: {str(e)}"

    @mcp.tool(description=load_prompt("move_tasks"))
    @log_interaction
    async def move_tasks(
        moves: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> str:
        move_list, single_move, error = normalize_batch_input(moves, "Move")
        if error:
            return error

        validation_errors = []
        for i, move_data in enumerate(move_list):
            validation_errors.extend(
                validate_required_fields(
                    move_data,
                    ["task_id", "from_project_id", "to_project_id"],
                    i,
                    "Move",
                )
            )

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        moved_tasks = []
        failed_tasks = []

        try:
            ticktick = ensure_client()
            for i, move_data in enumerate(move_list):
                try:
                    task_id = move_data["task_id"]
                    result = ticktick.move_task(
                        task_id=task_id,
                        from_project_id=move_data["from_project_id"],
                        to_project_id=move_data["to_project_id"],
                    )

                    if "error" in result:
                        failed_tasks.append(
                            f"Move {i + 1} (Task ID: {task_id}): {result['error']}"
                        )
                    else:
                        moved_tasks.append(
                            (i + 1, task_id, move_data["to_project_id"])
                        )
                except Exception as e:
                    failed_tasks.append(
                        f"Move {i + 1} (Task ID: {move_data.get('task_id', 'Unknown')}): {str(e)}"
                    )

            return format_batch_result(
                moved_tasks,
                failed_tasks,
                "moved",
                "task",
                single_move,
                single_success_formatter=lambda item: f"Task {item[1]} moved successfully. New project ID: {item[2]}",
                batch_item_formatter=lambda item: f"{item[0]}. Task ID: {item[1]} -> Project ID: {item[2]}",
            )

        except Exception as e:
            logger.error(f"Error in move_tasks: {e}")
            return f"Error during task move: {str(e)}"
