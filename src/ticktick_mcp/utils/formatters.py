"""
Formatting utilities for TickTick MCP.

This module provides functions for formatting tasks, projects, and lists
into human-readable strings for display in MCP responses.
"""

from typing import Dict, List
from .timezone import convert_utc_to_local


def format_task(task: Dict, show_local_time: bool = True) -> str:
    """Format a task into a human-readable string with optional timezone conversion."""
    formatted = f"ID: {task.get('id', 'No ID')}\n"
    formatted += f"Title: {task.get('title', 'No title')}\n"
    
    # Add project ID
    formatted += f"Project ID: {task.get('projectId', 'None')}\n"
    
    # Add dates with timezone conversion
    if task.get('startDate'):
        if show_local_time:
            formatted += f"Start Date: {convert_utc_to_local(task.get('startDate'), task.get('timeZone'))}\n"
        else:
            formatted += f"Start Date: {task.get('startDate')} (UTC)\n"
    
    if task.get('dueDate'):
        if show_local_time:
            formatted += f"Due Date: {convert_utc_to_local(task.get('dueDate'), task.get('timeZone'))}\n"
        else:
            formatted += f"Due Date: {task.get('dueDate')} (UTC)\n"
    
    # 显示任务的时区信息（如果有）
    if task.get('timeZone'):
        formatted += f"Task Timezone: {task.get('timeZone')}\n"
    
    # Add priority if available
    priority_map = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    priority = task.get('priority', 0)
    formatted += f"Priority: {priority_map.get(priority, str(priority))}\n"
    
    # Add status if available
    status = "Completed" if task.get('status') == 2 else "Active"
    formatted += f"Status: {status}\n"
    
    # Add content if available
    if task.get('content'):
        formatted += f"\nContent:\n{task.get('content')}\n"
    
    # Add subtasks if available
    items = task.get('items', [])
    if items:
        formatted += f"\nSubtasks ({len(items)}):\n"
        for i, item in enumerate(items, 1):
            status = "✓" if item.get('status') == 1 else "□"
            formatted += f"{i}. [{status}] {item.get('title', 'No title')}\n"
    
    return formatted


def format_project(project: Dict) -> str:
    """Format a project into a human-readable string."""
    formatted = f"Name: {project.get('name', 'No name')}\n"
    formatted += f"ID: {project.get('id', 'No ID')}\n"
    
    # Add color if available
    if project.get('color'):
        formatted += f"Color: {project.get('color')}\n"
    
    # Add view mode if available
    if project.get('viewMode'):
        formatted += f"View Mode: {project.get('viewMode')}\n"
    
    # Add closed status if available
    if 'closed' in project:
        formatted += f"Closed: {'Yes' if project.get('closed') else 'No'}\n"
    
    # Add kind if available
    if project.get('kind'):
        formatted += f"Kind: {project.get('kind')}\n"
    
    return formatted


def format_tasks(tasks: List[Dict], title: str = "Tasks", show_local_time: bool = True) -> str:
    """Format a list of tasks into a human-readable string."""
    if not tasks:
        return f"No {title.lower()} found."
    
    result = f"Found {len(tasks)} {title.lower()}:\n\n"
    
    for i, task in enumerate(tasks, 1):
        result += f"Task {i}:\n" + format_task(task, show_local_time) + "\n"
    
    return result


def format_projects(projects: List[Dict], title: str = "Projects") -> str:
    """Format a list of projects into a human-readable string."""
    if not projects:
        return f"No {title.lower()} found."
    
    result = f"Found {len(projects)} {title.lower()}:\n\n"
    
    for i, project in enumerate(projects, 1):
        result += f"Project {i}:\n" + format_project(project) + "\n"
    
    return result


def format_habit(habit: Dict) -> str:
    """Format a habit into a human-readable string.

    Only LLM-relevant fields are shown; etag, sortOrder, timestamps and other
    noise are intentionally omitted to keep the tool result compact.
    """
    formatted = f"ID: {habit.get('id', 'No ID')}\n"
    formatted += f"Name: {habit.get('name', 'No name')}\n"

    if habit.get('color'):
        formatted += f"Color: {habit.get('color')}\n"
    if habit.get('type'):
        formatted += f"Type: {habit.get('type')}\n"
    if habit.get('goal') is not None:
        formatted += f"Goal: {habit.get('goal')}\n"
    if habit.get('step') is not None:
        formatted += f"Step: {habit.get('step')}\n"
    if habit.get('unit'):
        formatted += f"Unit: {habit.get('unit')}\n"
    if habit.get('repeatRule'):
        formatted += f"Repeat Rule: {habit.get('repeatRule')}\n"

    status_map = {0: "Active", 1: "Archived"}
    status = habit.get('status')
    formatted += f"Status: {status_map.get(status, str(status))}\n"

    if habit.get('encouragement'):
        formatted += f"Encouragement: {habit.get('encouragement')}\n"
    if habit.get('totalCheckIns') is not None:
        formatted += f"Total Check-ins: {habit.get('totalCheckIns')}\n"

    reminders = habit.get('reminders') or []
    if reminders:
        formatted += f"Reminders: {', '.join(reminders)}\n"

    return formatted


def format_habits(habits: List[Dict], title: str = "Habits") -> str:
    """Format a list of habits into a human-readable string."""
    if not habits:
        return f"No {title.lower()} found."

    result = f"Found {len(habits)} {title.lower()}:\n\n"
    for i, habit in enumerate(habits, 1):
        result += f"Habit {i}:\n" + format_habit(habit) + "\n"

    return result


def format_habit_checkin(checkin: Dict) -> str:
    """Format a habit check-in result into a human-readable string."""
    formatted = f"Habit ID: {checkin.get('habitId', 'No ID')}\n"
    if checkin.get('year') is not None:
        formatted += f"Year: {checkin.get('year')}\n"

    entries = checkin.get('checkins', [])
    if entries:
        formatted += f"Check-ins ({len(entries)}):\n"
        for i, entry in enumerate(entries, 1):
            value = entry.get('value', 0)
            goal = entry.get('goal', 0)
            formatted += f"{i}. Stamp: {entry.get('stamp')} | Value: {value}/{goal}\n"
    else:
        formatted += "Check-ins: None\n"

    return formatted


def format_habit_checkins(checkins: List[Dict]) -> str:
    """Format a list of habit check-in results into a human-readable string."""
    if not checkins:
        return "No check-ins found."

    result = f"Found {len(checkins)} habit check-in record(s):\n\n"
    for i, checkin in enumerate(checkins, 1):
        result += f"Record {i}:\n" + format_habit_checkin(checkin) + "\n"

    return result
