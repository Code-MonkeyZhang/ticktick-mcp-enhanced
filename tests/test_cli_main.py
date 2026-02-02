"""
Tests for CLI main module.
"""

import pytest


class TestMainCLI:
    """Tests for main CLI entry point."""

    def test_cli_main_module_exists(self):
        """Test that main CLI module exists and has app."""
        from ticktick_mcp.cli import main

        assert hasattr(main, "app")
        assert main.app is not None

    def test_cli_version_defined(self):
        """Test that version is defined."""
        from ticktick_mcp.cli import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert "." in __version__
