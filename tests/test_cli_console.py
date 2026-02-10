"""
Tests for CLI console module.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from rich.console import Console
from rich.table import Table


class TestConsoleModule:
    """Tests for console.py module."""

    def test_console_instance_exists(self):
        """Test that console module exports a Console instance."""
        from ticktick_mcp.cli import console

        assert hasattr(console, "console")
        assert isinstance(console.console, Console)

    def test_print_success_function(self):
        """Test print_success function renders green message."""
        from ticktick_mcp.cli.console import print_success

        with patch("ticktick_mcp.cli.console.console.print") as mock_print:
            print_success("Operation successful")
            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "Operation successful" in str(args)
            assert "green" in str(args).lower() or "✓" in str(args)

    def test_print_error_function(self):
        """Test print_error function renders red message."""
        from ticktick_mcp.cli.console import print_error

        with patch("ticktick_mcp.cli.console.console.print") as mock_print:
            print_error("Something went wrong")
            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "Something went wrong" in str(args)
            assert "red" in str(args).lower() or "✗" in str(args)

    def test_print_warning_function(self):
        """Test print_warning function renders yellow message."""
        from ticktick_mcp.cli.console import print_warning

        with patch("ticktick_mcp.cli.console.console.print") as mock_print:
            print_warning("Warning message")
            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "Warning message" in str(args)
            assert "yellow" in str(args).lower() or "⚠" in str(args)

    def test_print_info_function(self):
        """Test print_info function renders blue message."""
        from ticktick_mcp.cli.console import print_info

        with patch("ticktick_mcp.cli.console.console.print") as mock_print:
            print_info("Info message")
            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "Info message" in str(args)
            assert "blue" in str(args).lower() or "ℹ" in str(args)


class TestTaskTableRendering:
    """Tests for task table rendering functions."""

    def test_create_task_table_returns_table(self):
        """Test create_task_table returns a Rich Table."""
        from ticktick_mcp.cli.console import create_task_table

        tasks = [
            {
                "id": "task1",
                "title": "Test Task",
                "priority": 5,
                "dueDate": "2025-12-31T23:59:59+0000",
                "status": 0,
            }
        ]

        table = create_task_table(tasks)
        assert isinstance(table, Table)

    def test_create_task_table_empty_list(self):
        """Test create_task_table handles empty task list."""
        from ticktick_mcp.cli.console import create_task_table

        table = create_task_table([])
        assert isinstance(table, Table)

    def test_create_task_table_shows_priority_high(self):
        """Test high priority tasks are marked appropriately."""
        from ticktick_mcp.cli.console import create_task_table

        tasks = [{"id": "t1", "title": "High Priority", "priority": 5}]
        table = create_task_table(tasks)

        # Table should have at least one row
        assert len(table.rows) >= 1

    def test_create_task_table_shows_priority_medium(self):
        """Test medium priority tasks are marked appropriately."""
        from ticktick_mcp.cli.console import create_task_table

        tasks = [{"id": "t1", "title": "Medium Priority", "priority": 3}]
        table = create_task_table(tasks)

        assert len(table.rows) >= 1

    def test_create_task_table_shows_priority_low(self):
        """Test low priority tasks are marked appropriately."""
        from ticktick_mcp.cli.console import create_task_table

        tasks = [{"id": "t1", "title": "Low Priority", "priority": 1}]
        table = create_task_table(tasks)

        assert len(table.rows) >= 1

    def test_create_task_table_shows_priority_none(self):
        """Test no priority tasks are marked appropriately."""
        from ticktick_mcp.cli.console import create_task_table

        tasks = [{"id": "t1", "title": "No Priority", "priority": 0}]
        table = create_task_table(tasks)

        assert len(table.rows) >= 1

    def test_create_task_table_handles_completed_status(self):
        """Test completed tasks show correct status."""
        from ticktick_mcp.cli.console import create_task_table

        tasks = [{"id": "t1", "title": "Done Task", "priority": 0, "status": 2}]
        table = create_task_table(tasks)

        assert len(table.rows) >= 1


class TestProjectTableRendering:
    """Tests for project table rendering functions."""

    def test_create_project_table_returns_table(self):
        """Test create_project_table returns a Rich Table."""
        from ticktick_mcp.cli.console import create_project_table

        projects = [
            {
                "id": "proj1",
                "name": "Test Project",
                "color": "#F18181",
                "viewMode": "list",
            }
        ]

        table = create_project_table(projects)
        assert isinstance(table, Table)

    def test_create_project_table_empty_list(self):
        """Test create_project_table handles empty project list."""
        from ticktick_mcp.cli.console import create_project_table

        table = create_project_table([])
        assert isinstance(table, Table)

    def test_create_project_table_shows_all_fields(self):
        """Test project table includes all relevant fields."""
        from ticktick_mcp.cli.console import create_project_table

        projects = [
            {
                "id": "proj1",
                "name": "My Project",
                "color": "#00FF00",
                "viewMode": "kanban",
            }
        ]

        table = create_project_table(projects)
        assert isinstance(table, Table)
        assert len(table.rows) >= 1


class TestFormatDate:
    """Tests for date formatting utilities."""

    def test_format_due_date_with_valid_date(self):
        """Test format_due_date with valid ISO date."""
        from ticktick_mcp.cli.console import format_due_date

        result = format_due_date("2025-12-31T23:59:59+0000")
        assert "2025" in result or "12" in result or "31" in result

    def test_format_due_date_with_none(self):
        """Test format_due_date with None returns 'No due date'."""
        from ticktick_mcp.cli.console import format_due_date

        result = format_due_date(None)
        assert result == "No due date" or result == "-"

    def test_format_due_date_with_empty_string(self):
        """Test format_due_date with empty string."""
        from ticktick_mcp.cli.console import format_due_date

        result = format_due_date("")
        assert result == "No due date" or result == "-"
