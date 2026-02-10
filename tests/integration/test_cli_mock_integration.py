"""
Mock integration tests for TickTick CLI.

These tests use mocked API responses to test CLI behavior without real credentials.
"""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner


# Always run these tests (no skip condition)
class TestCLIMockIntegration:
    """Mock integration tests that don't require real API calls."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock TickTick client."""
        client = MagicMock()

        # Mock auth
        client.auth.is_authenticated.return_value = True
        client.auth.config = {"name": "TickTick Test"}

        # Mock projects
        client.get_all_projects.return_value = [
            {
                "id": "proj-1",
                "name": "Test Project 1",
                "color": "#FF0000",
                "viewMode": "list",
            },
            {"id": "inbox", "name": "Inbox", "color": "#F18181", "viewMode": "list"},
        ]

        # Mock project with data
        client.get_project_with_data.return_value = {
            "project": {"id": "proj-1", "name": "Test Project 1"},
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Test Task 1",
                    "priority": 5,
                    "status": 0,
                    "dueDate": "2025-12-31T23:59:59+0000",
                },
                {
                    "id": "task-2",
                    "title": "Test Task 2",
                    "priority": 3,
                    "status": 1,
                    "dueDate": None,
                },
            ],
        }

        # Mock create project
        client.create_project.return_value = {
            "id": "new-proj-123",
            "name": "New Project",
            "color": "#00FF00",
        }

        # Mock create task
        client.create_task.return_value = {
            "id": "new-task-456",
            "title": "New Task",
            "project_id": "proj-1",
        }

        # Mock complete task
        client.complete_task.return_value = {"success": True}

        # Mock delete task
        client.delete_task.return_value = {"success": True}

        # Mock delete project
        client.delete_project.return_value = {"success": True}

        return client

    def test_projects_list_with_mock(self, mock_client):
        """Test listing projects with mocked client."""
        from ticktick_mcp.cli.commands.projects import app

        runner = CliRunner()

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Test Project 1" in result.output or "Projects" in result.output

    def test_tasks_list_with_mock(self, mock_client):
        """Test listing tasks with mocked client."""
        from ticktick_mcp.cli.commands.tasks import app

        runner = CliRunner()

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Test Task 1" in result.output or len(result.output) > 0

    def test_create_project_with_mock(self, mock_client):
        """Test creating project with mocked client."""
        from ticktick_mcp.cli.commands.projects import app

        runner = CliRunner()

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(
                    app, ["create", "My New Project", "--color", "#00FF00"]
                )

        assert result.exit_code == 0
        mock_client.create_project.assert_called_once()

    def test_create_task_with_mock(self, mock_client):
        """Test creating task with mocked client."""
        from ticktick_mcp.cli.commands.tasks import app

        runner = CliRunner()

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(
                    app,
                    [
                        "create",
                        "My New Task",
                        "--project",
                        "proj-1",
                        "--priority",
                        "high",
                    ],
                )

        assert result.exit_code == 0
        mock_client.create_task.assert_called_once()

    def test_complete_task_with_mock(self, mock_client):
        """Test completing task with mocked client."""
        from ticktick_mcp.cli.commands.tasks import app

        runner = CliRunner()

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(
                    app, ["complete", "task-1", "--project", "proj-1"]
                )

        assert result.exit_code == 0
        mock_client.complete_task.assert_called_once_with("proj-1", "task-1")

    def test_auth_status_authenticated(self, mock_client):
        """Test auth status when authenticated."""
        from ticktick_mcp.cli.commands.auth import app

        runner = CliRunner()

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Authenticated" in result.output

    def test_auth_status_not_authenticated(self):
        """Test auth status when not authenticated."""
        from ticktick_mcp.cli.commands.auth import app

        runner = CliRunner()

        mock_client = MagicMock()
        mock_client.auth.is_authenticated.return_value = False

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Not authenticated" in result.output

    def test_full_workflow_mock(self, mock_client):
        """Test full workflow: create project -> create task -> complete task -> delete."""
        from ticktick_mcp.cli.commands.projects import app as projects_app
        from ticktick_mcp.cli.commands.tasks import app as tasks_app

        runner = CliRunner()

        # Step 1: Create project
        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(
                    projects_app, ["create", "Workflow Test Project"]
                )

        assert result.exit_code == 0

        # Step 2: Create task
        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(
                    tasks_app,
                    [
                        "create",
                        "Workflow Test Task",
                        "--project",
                        "new-proj-123",
                        "--priority",
                        "high",
                    ],
                )

        assert result.exit_code == 0

        # Step 3: Complete task
        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(
                    tasks_app, ["complete", "new-task-456", "--project", "new-proj-123"]
                )

        assert result.exit_code == 0

        # Verify all operations were called
        mock_client.create_project.assert_called()
        mock_client.create_task.assert_called()
        mock_client.complete_task.assert_called()


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_api_error_handling(self):
        """Test handling of API errors."""
        from ticktick_mcp.cli.commands.projects import app

        runner = CliRunner()

        mock_client = MagicMock()
        mock_client.auth.is_authenticated.return_value = True
        mock_client.get_all_projects.return_value = {
            "error": "API Error: Rate limit exceeded"
        }

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(app, ["list"])

        # Should handle error gracefully
        assert (
            result.exit_code == 1
            or "error" in result.output.lower()
            or "Error" in result.output
        )

    def test_network_error_handling(self):
        """Test handling of network errors."""
        from ticktick_mcp.cli.commands.projects import app

        runner = CliRunner()

        mock_client = MagicMock()
        mock_client.auth.is_authenticated.return_value = True
        mock_client.get_all_projects.side_effect = Exception("Connection timeout")

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(app, ["list"])

        # Should handle error gracefully
        assert result.exit_code == 1 or "error" in result.output.lower()

    def test_invalid_project_id(self):
        """Test handling of invalid project ID."""
        from ticktick_mcp.cli.commands.tasks import app

        runner = CliRunner()

        mock_client = MagicMock()
        mock_client.auth.is_authenticated.return_value = True
        mock_client.create_task.return_value = {"error": "Project not found"}

        with patch("ticktick_mcp.client_manager.get_client", return_value=mock_client):
            with patch("ticktick_mcp.client_manager.initialize_client"):
                result = runner.invoke(
                    app, ["create", "Test Task", "--project", "invalid-project-id"]
                )

        # Should handle error gracefully
        assert result.exit_code == 1 or "error" in result.output.lower()
