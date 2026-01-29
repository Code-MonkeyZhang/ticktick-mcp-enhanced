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
