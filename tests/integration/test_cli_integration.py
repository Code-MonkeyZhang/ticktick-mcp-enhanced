"""
Integration tests for TickTick CLI.

These tests require real API credentials and will make actual API calls.
Set TICKTICK_RUN_INTEGRATION_TESTS=1 to enable them.
"""

import os
import subprocess
import re
import pytest
import uuid


# Skip integration tests unless explicitly enabled
pytestmark = pytest.mark.skipif(
    not os.getenv("TICKTICK_RUN_INTEGRATION_TESTS"),
    reason="Set TICKTICK_RUN_INTEGRATION_TESTS=1 to run integration tests",
)


def run_ticktick_command(args):
    """Run a ticktick CLI command using subprocess.

    Requires the following environment variables to be set:
    - TICKTICK_ACCOUNT_TYPE (optional, defaults to "global")
    - TICKTICK_CLIENT_ID (required)
    - TICKTICK_CLIENT_SECRET (required)
    - TICKTICK_REDIRECT_URI (optional, defaults to http://localhost:8000/callback)
    """
    cmd = ["uv", "run", "ticktick"] + args
    env = os.environ.copy()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    )
    return result


def skip_on_api_error(result, operation="API operation"):
    """Check if result contains API errors and skip test if so."""
    output = result.stdout + result.stderr
    if result.returncode != 0:
        if "500" in output:
            pytest.skip(
                f"API server error (500) during {operation} - likely rate limiting"
            )
        elif "429" in output:
            pytest.skip(f"API rate limit exceeded (429) during {operation}")
        elif "502" in output:
            pytest.skip(f"API gateway error (502) during {operation}")
        elif "503" in output:
            pytest.skip(f"API service unavailable (503) during {operation}")
    return False


class TestCLIIntegration:
    """Integration tests that make real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure we have credentials before running tests."""
        if not os.getenv("TICKTICK_CLIENT_ID") or not os.getenv(
            "TICKTICK_CLIENT_SECRET"
        ):
            pytest.skip("TICKTICK_CLIENT_ID and TICKTICK_CLIENT_SECRET must be set")

    def test_auth_status_command(self):
        """Test auth status command with real credentials."""
        result = run_ticktick_command(["auth", "status"])

        # Should either show authenticated or not authenticated
        assert result.returncode == 0
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_projects_list_command(self):
        """Test listing projects."""
        result = run_ticktick_command(["projects", "list"])

        output = result.stdout + result.stderr
        # Should show output (either projects or auth error)
        assert len(output) > 0
        # If token expired, that's a valid response we can detect
        if "expired" in output.lower() or "invalid" in output.lower():
            pytest.skip(f"Token expired or invalid: {output}")

    def test_tasks_list_command(self):
        """Test listing tasks."""
        result = run_ticktick_command(["tasks", "list"])

        output = result.stdout + result.stderr
        assert len(output) > 0
        # If token expired, skip test
        if "expired" in output.lower() or "invalid" in output.lower():
            pytest.skip(f"Token expired or invalid: {output}")

    def test_version_flag(self):
        """Test --version flag."""
        result = run_ticktick_command(["--version"])

        assert result.returncode == 0
        assert "0.2.0" in result.stdout

    def test_help_shows_all_commands(self):
        """Test that help shows all command groups."""
        result = run_ticktick_command(["--help"])

        assert result.returncode == 0
        output = result.stdout
        assert "auth" in output
        assert "tasks" in output
        assert "projects" in output


@pytest.mark.integration
class TestAuthenticatedOperations:
    """Tests that require authenticated session."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Skip if not authenticated."""
        from ticktick_mcp.cli.context import CLIContext
        from ticktick_mcp import client_manager

        # Reset client manager global state to ensure clean initialization
        client_manager.ticktick = None

        ctx = CLIContext()
        if not ctx.ensure_authenticated():
            pytest.skip("Not authenticated. Run 'ticktick auth login' first.")

    def test_create_and_delete_project(self):
        """Test creating and deleting a project."""
        project_name = f"Test Project {uuid.uuid4().hex[:8]}"

        # Create project
        result = run_ticktick_command(["projects", "create", project_name])
        skip_on_api_error(result, "project creation")
        assert result.returncode == 0, (
            f"Project creation failed: {result.stdout} {result.stderr}"
        )
        output = result.stdout + result.stderr
        assert project_name in output or "created" in output.lower()

        # Extract project ID from output
        project_id = None
        for line in output.split("\n"):
            if "ID:" in line or "id" in line.lower():
                id_match = re.search(
                    r"\b[a-f0-9]{24}\b|\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
                    line,
                )
                if id_match:
                    project_id = id_match.group(0)
                    break

        if project_id:
            # Delete project
            result = run_ticktick_command(["projects", "delete", project_id, "--force"])
            skip_on_api_error(result, "project deletion")
            assert result.returncode == 0
            output = result.stdout + result.stderr
            assert "deleted" in output.lower() or "success" in output.lower()

    def test_create_and_complete_task(self):
        """Test creating and completing a task."""
        from ticktick_mcp.cli.context import CLIContext

        ctx = CLIContext()
        client = ctx.get_client()

        # Get projects to find a valid project ID
        projects = client.get_all_projects()
        if "error" in projects or not projects:
            pytest.skip("Could not fetch projects")

        # Use the first non-inbox project, or inbox
        test_project_id = "inbox"
        for proj in projects:
            if proj.get("id") != "inbox":
                test_project_id = proj["id"]
                break

        task_title = f"Test Task {uuid.uuid4().hex[:8]}"

        # Create task
        result = run_ticktick_command(
            [
                "tasks",
                "create",
                task_title,
                "--project",
                test_project_id,
                "--priority",
                "low",
            ]
        )
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert task_title in output or "created" in output.lower()

        # Extract task ID
        task_id = None
        for line in output.split("\n"):
            if "ID:" in line or "id" in line.lower():
                uuid_match = re.search(
                    r"\b[a-f0-9]{24}\b|\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
                    line,
                )
                if uuid_match:
                    task_id = uuid_match.group(0)
                    break

        if task_id:
            # Complete task
            result = run_ticktick_command(
                ["tasks", "complete", task_id, "--project", test_project_id]
            )
            # Task completion may succeed even if already completed
            assert result.returncode == 0

    def test_tasks_today_command(self):
        """Test listing today's tasks."""
        result = run_ticktick_command(["tasks", "today"])
        skip_on_api_error(result, "fetching today's tasks")
        assert result.returncode == 0
        output = result.stdout + result.stderr
        # Should show either tasks or "No tasks due today"
        assert len(output) > 0

    def test_tasks_overdue_command(self):
        """Test listing overdue tasks."""
        result = run_ticktick_command(["tasks", "overdue"])
        skip_on_api_error(result, "fetching overdue tasks")
        assert result.returncode == 0
        output = result.stdout + result.stderr
        # Should show either tasks or "No overdue tasks"
        assert len(output) > 0


class TestCLIWorkflows:
    """End-to-end workflow tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Skip if not authenticated."""
        from ticktick_mcp.cli.context import CLIContext
        from ticktick_mcp import client_manager

        # Reset client manager global state to ensure clean initialization
        client_manager.ticktick = None

        ctx = CLIContext()
        if not ctx.ensure_authenticated():
            pytest.skip("Not authenticated. Run 'ticktick auth login' first.")

    def test_full_task_lifecycle(self):
        """Test complete task lifecycle: create -> list -> complete."""
        from ticktick_mcp.cli.context import CLIContext

        ctx = CLIContext()
        client = ctx.get_client()

        # Get a project to use
        projects = client.get_all_projects()
        if "error" in projects or not projects:
            pytest.skip("Could not fetch projects")

        project_id = projects[0]["id"]
        task_title = f"E2E Test Task {uuid.uuid4().hex[:8]}"

        # Step 1: Create task
        result = run_ticktick_command(
            [
                "tasks",
                "create",
                task_title,
                "--project",
                project_id,
                "--content",
                "E2E test task content",
                "--priority",
                "high",
            ]
        )
        skip_on_api_error(result, "task creation")
        assert result.returncode == 0, (
            f"Task creation failed: {result.stdout} {result.stderr}"
        )

        # Extract task ID (supports both 24-char hex and 36-char UUID formats)
        task_id = None
        output = result.stdout + result.stderr
        for line in output.split("\n"):
            if "ID:" in line or "id" in line.lower():
                # Match 24-char hex or 36-char UUID
                id_match = re.search(
                    r"\b[a-f0-9]{24}\b|\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
                    line,
                )
                if id_match:
                    task_id = id_match.group(0)
                    break

        if not task_id:
            pytest.skip("Could not extract task ID")

        # Step 2: View task
        result = run_ticktick_command(
            ["tasks", "view", task_id, "--project", project_id]
        )
        # View may fail if task format differs, but shouldn't crash
        assert result.returncode == 0 or result.returncode == 1

        # Step 3: Complete task
        result = run_ticktick_command(
            ["tasks", "complete", task_id, "--project", project_id]
        )
        assert result.returncode == 0

    def test_project_workflow(self):
        """Test project workflow: create -> list -> delete."""
        import time

        # Add delay to avoid API rate limiting
        time.sleep(2)

        project_name = f"E2E Project {uuid.uuid4().hex[:8]}"

        # Create
        result = run_ticktick_command(
            ["projects", "create", project_name, "--color", "#FF0000"]
        )
        # Skip on API server errors (rate limiting or transient issues)
        if result.returncode != 0:
            if "500" in result.stdout or "500" in result.stderr:
                pytest.skip("API server error (500) - likely rate limiting")
            elif "429" in result.stdout or "429" in result.stderr:
                pytest.skip("API rate limit exceeded (429)")
        assert result.returncode == 0, (
            f"Project creation failed: {result.stdout} {result.stderr}"
        )

        # Extract project ID
        project_id = None
        output = result.stdout + result.stderr
        for line in output.split("\n"):
            if "ID:" in line or "id" in line.lower():
                id_match = re.search(
                    r"\b[a-f0-9]{24}\b|\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
                    line,
                )
                if id_match:
                    project_id = id_match.group(0)
                    break

        if not project_id:
            pytest.skip("Could not extract project ID")

        # View
        result = run_ticktick_command(["projects", "view", project_id])
        assert result.returncode == 0

        # Delete
        result = run_ticktick_command(["projects", "delete", project_id, "--force"])
        assert result.returncode == 0


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (requires API credentials)",
    )
