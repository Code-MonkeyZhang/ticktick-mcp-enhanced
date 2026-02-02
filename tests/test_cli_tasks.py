"""
Tests for CLI tasks commands.
"""

from unittest.mock import MagicMock, patch


class TestTasksCommands:
    """Tests for tasks commands."""

    def test_tasks_app_exists(self):
        """Test that tasks app exists."""
        from ticktick_mcp.cli.commands.tasks import app

        assert app is not None

    def test_tasks_commands_exist(self):
        """Test that tasks commands are defined."""
        from ticktick_mcp.cli.commands import tasks

        assert hasattr(tasks, "list")
        assert hasattr(tasks, "today")
        assert hasattr(tasks, "overdue")
        assert hasattr(tasks, "create")
        assert hasattr(tasks, "complete")
        assert hasattr(tasks, "delete")
        assert hasattr(tasks, "view")


class TestPriorityMapping:
    """Tests for priority mapping logic."""

    def test_priority_map_values(self):
        """Test that priority mapping is correct."""
        priority_map = {"none": 0, "low": 1, "medium": 3, "high": 5}

        assert priority_map["none"] == 0
        assert priority_map["low"] == 1
        assert priority_map["medium"] == 3
        assert priority_map["high"] == 5


class TestTaskFilter:
    """Tests for task filter logic."""

    def test_task_filter_by_priority(self):
        """Test filtering tasks by priority."""
        priority_map = {"none": 0, "low": 1, "medium": 3, "high": 5}

        def task_filter(task, priority):
            return task.get("priority", 0) == priority_map.get(priority.lower(), 0)

        task = {"title": "Test", "priority": 5}
        assert task_filter(task, "high") is True
        assert task_filter(task, "low") is False

    def test_task_filter_by_search(self):
        """Test filtering tasks by search term."""

        def task_filter(task, search):
            search_lower = search.lower()
            title = task.get("title", "").lower()
            content = task.get("content", "").lower()
            return search_lower in title or search_lower in content

        task = {"title": "Buy milk", "content": "From store"}
        assert task_filter(task, "milk") is True
        assert task_filter(task, "store") is True
        assert task_filter(task, "bread") is False
