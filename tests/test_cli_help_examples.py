"""Tests for CLI help examples integration."""

import subprocess
import sys


def test_ticktick_help_shows_examples():
    """Test that ticktick -h shows usage examples."""
    result = subprocess.run(
        [sys.executable, "-m", "ticktick_mcp.cli.main", "-h"],
        capture_output=True,
        text=True,
    )

    # Should exit with code 0
    assert result.returncode == 0

    output = result.stdout
    # Remove whitespace that may interfere with matching
    output_clean = output.replace("\n", " ").replace("\r", " ")

    # Check for key examples in the help output
    assert "ticktick list" in output_clean, "Should show 'ticktick list' example"
    assert "today" in output_clean, "Should show 'today' example"
    assert "overdue" in output_clean, "Should show 'overdue' example"
    assert "projects" in output_clean, "Should show 'projects' example"
    assert "auth login" in output_clean, "Should show 'auth login' example"


def test_ticktick_help_shows_task_examples():
    """Test that help shows task management examples."""
    result = subprocess.run(
        [sys.executable, "-m", "ticktick_mcp.cli.main", "-h"],
        capture_output=True,
        text=True,
    )

    output = result.stdout.replace("\n", " ").replace("\r", " ")

    # Task management examples
    assert "tasks create" in output, "Should show task create example"
    assert "tasks complete" in output, "Should show task complete example"
    assert "tasks delete" in output, "Should show task delete example"


def test_ticktick_help_shows_filter_examples():
    """Test that help shows filtering examples."""
    result = subprocess.run(
        [sys.executable, "-m", "ticktick_mcp.cli.main", "-h"],
        capture_output=True,
        text=True,
    )

    output = result.stdout.replace("\n", " ").replace("\r", " ")

    # Filtering examples
    assert "priority" in output, "Should show priority filter example"
    assert "-s" in output or "search" in output, "Should show search filter example"
    assert "Filtering" in output or "Search" in output, "Should show filtering section"
