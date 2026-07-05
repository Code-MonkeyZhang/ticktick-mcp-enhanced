"""
MCP tools for TickTick integration.

This package contains all the MCP tool definitions organized by functionality:
- project_tools: Project management tools
- task_tools: Task CRUD operations
- query_tools: Task querying and filtering tools
- habit_tools: Habit management tools
"""

from .project_tools import register_project_tools
from .task_tools import register_task_tools
from .query_tools import register_query_tools
from .habit_tools import register_habit_tools

__all__ = [
    'register_project_tools',
    'register_task_tools',
    'register_query_tools',
    'register_habit_tools'
]
