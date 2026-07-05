"""
Habit management tools for TickTick MCP.

This module contains MCP tools for managing TickTick habits, including
listing, creating, updating, checking in, and querying check-in history.
"""

import logging
from typing import Any, Dict, List, Union

from mcp.server.fastmcp import FastMCP

from ..client_manager import ensure_client
from ..utils.formatters import (
    format_habit,
    format_habits,
    format_habit_checkin,
    format_habit_checkins,
)
from ..utils.logging_utils import log_interaction
from ..utils.timezone import date_to_stamp
from ..utils.validators import (
    build_habit_payload,
    format_batch_result,
    normalize_batch_input,
    validate_habit_data,
    validate_required_fields,
)
from .prompts import load_prompt

logger = logging.getLogger(__name__)


def register_habit_tools(mcp: FastMCP):
    """Register all habit-related MCP tools."""

    @mcp.tool(description=load_prompt("get_all_habits"))
    @log_interaction
    async def get_all_habits() -> str:
        try:
            ticktick = ensure_client()
            habits = ticktick.get_all_habits()
            if isinstance(habits, dict) and "error" in habits:
                return f"Error fetching habits: {habits['error']}"

            return format_habits(habits)
        except Exception as e:
            logger.error(f"Error in get_all_habits: {e}")
            return f"Error retrieving habits: {str(e)}"

    @mcp.tool(description=load_prompt("get_habit"))
    @log_interaction
    async def get_habit(habit_id: str) -> str:
        try:
            ticktick = ensure_client()
            habit = ticktick.get_habit(habit_id)
            if isinstance(habit, dict) and "error" in habit:
                return f"Error fetching habit: {habit['error']}"

            return format_habit(habit)
        except Exception as e:
            logger.error(f"Error in get_habit: {e}")
            return f"Error retrieving habit: {str(e)}"

    @mcp.tool(description=load_prompt("create_habits"))
    @log_interaction
    async def create_habits(
        habits: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> str:
        habit_list, single_habit, error = normalize_batch_input(habits, "Habit")
        if error:
            return error

        validation_errors = []
        for i, habit_data in enumerate(habit_list):
            err = validate_habit_data(habit_data, i)
            if err:
                validation_errors.append(err)

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        created_habits = []
        failed_habits = []

        try:
            ticktick = ensure_client()
            for i, habit_data in enumerate(habit_list):
                try:
                    name = habit_data["name"]
                    result = ticktick.create_habit(build_habit_payload(habit_data))

                    if "error" in result:
                        failed_habits.append(
                            f"Habit {i + 1} ('{name}'): {result['error']}"
                        )
                    else:
                        created_habits.append((i + 1, name, result))
                except Exception as e:
                    failed_habits.append(
                        f"Habit {i + 1} ('{habit_data.get('name', 'Unknown')}'): {str(e)}"
                    )

            return format_batch_result(
                created_habits,
                failed_habits,
                "created",
                "habit",
                single_habit,
                single_success_formatter=lambda item: f"Habit created successfully:\n\n{format_habit(item[2])}",
                batch_item_formatter=lambda item: f"{item[0]}. {item[1]} (ID: {item[2].get('id', 'Unknown')})",
            )

        except Exception as e:
            logger.error(f"Error in create_habits: {e}")
            return f"Error during habit creation: {str(e)}"

    @mcp.tool(description=load_prompt("update_habits"))
    @log_interaction
    async def update_habits(
        habits: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> str:
        habit_list, single_habit, error = normalize_batch_input(habits, "Habit")
        if error:
            return error

        validation_errors = []
        for i, habit_data in enumerate(habit_list):
            validation_errors.extend(
                validate_required_fields(habit_data, ["habit_id"], i, "Habit")
            )

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        updated_habits = []
        failed_habits = []

        try:
            ticktick = ensure_client()
            for i, habit_data in enumerate(habit_list):
                try:
                    habit_id = habit_data["habit_id"]
                    result = ticktick.update_habit(
                        habit_id, build_habit_payload(habit_data)
                    )

                    if "error" in result:
                        failed_habits.append(
                            f"Habit {i + 1} (ID: {habit_id}): {result['error']}"
                        )
                    else:
                        updated_habits.append((i + 1, habit_id, result))
                except Exception as e:
                    failed_habits.append(
                        f"Habit {i + 1} (ID: {habit_data.get('habit_id', 'Unknown')}): {str(e)}"
                    )

            return format_batch_result(
                updated_habits,
                failed_habits,
                "updated",
                "habit",
                single_habit,
                single_success_formatter=lambda item: f"Habit updated successfully:\n\n{format_habit(item[2])}",
                batch_item_formatter=lambda item: f"{item[0]}. {item[2].get('name', 'Unknown')} (ID: {item[1]})",
            )

        except Exception as e:
            logger.error(f"Error in update_habits: {e}")
            return f"Error during habit update: {str(e)}"

    @mcp.tool(description=load_prompt("checkin_habits"))
    @log_interaction
    async def checkin_habits(
        checkins: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> str:
        checkin_list, single_checkin, error = normalize_batch_input(
            checkins, "Check-in"
        )
        if error:
            return error

        validation_errors = []
        for i, checkin_data in enumerate(checkin_list):
            validation_errors.extend(
                validate_required_fields(
                    checkin_data, ["habit_id"], i, "Check-in"
                )
            )

        if validation_errors:
            return "Validation errors found:\n" + "\n".join(validation_errors)

        completed_checkins = []
        failed_checkins = []

        try:
            ticktick = ensure_client()
            for i, checkin_data in enumerate(checkin_list):
                try:
                    habit_id = checkin_data["habit_id"]
                    # date is optional and defaults to today via date_to_stamp
                    stamp = date_to_stamp(checkin_data.get("date"))
                    result = ticktick.checkin_habit(
                        habit_id=habit_id,
                        stamp=stamp,
                        value=checkin_data.get("value", 1.0),
                        goal=checkin_data.get("goal", 1.0),
                        status=checkin_data.get("status"),
                    )

                    if "error" in result:
                        failed_checkins.append(
                            f"Check-in {i + 1} (Habit ID: {habit_id}): {result['error']}"
                        )
                    else:
                        completed_checkins.append((i + 1, habit_id, result))
                except Exception as e:
                    failed_checkins.append(
                        f"Check-in {i + 1} (Habit ID: {checkin_data.get('habit_id', 'Unknown')}): {str(e)}"
                    )

            return format_batch_result(
                completed_checkins,
                failed_checkins,
                "checked-in",
                "check-in",
                single_checkin,
                single_success_formatter=lambda item: f"Check-in recorded successfully:\n\n{format_habit_checkin(item[2])}",
                batch_item_formatter=lambda item: f"{item[0]}. Habit ID: {item[1]} (stamp recorded)",
            )

        except Exception as e:
            logger.error(f"Error in checkin_habits: {e}")
            return f"Error during habit check-in: {str(e)}"

    @mcp.tool(description=load_prompt("get_habit_checkins"))
    @log_interaction
    async def get_habit_checkins(
        habit_ids: Union[str, List[str]],
        from_date: int,
        to_date: int,
    ) -> str:
        # Accept either a single habit ID or a list; normalize to a list.
        if isinstance(habit_ids, str):
            id_list = [habit_ids]
        else:
            id_list = habit_ids

        if not id_list:
            return "No habit IDs provided."

        try:
            ticktick = ensure_client()
            checkins = ticktick.get_habit_checkins(
                habit_ids=id_list, from_stamp=from_date, to_stamp=to_date
            )
            if isinstance(checkins, dict) and "error" in checkins:
                return f"Error fetching check-ins: {checkins['error']}"

            return format_habit_checkins(checkins)
        except Exception as e:
            logger.error(f"Error in get_habit_checkins: {e}")
            return f"Error retrieving habit check-ins: {str(e)}"
