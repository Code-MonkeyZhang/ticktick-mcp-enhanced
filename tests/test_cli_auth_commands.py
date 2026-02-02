"""
Tests for CLI auth commands.
"""

from unittest.mock import MagicMock, patch


class TestAuthCommands:
    """Tests for authentication commands."""

    def test_auth_app_exists(self):
        """Test that auth app exists."""
        from ticktick_mcp.cli.commands.auth import app

        assert app is not None

    def test_auth_commands_exist(self):
        """Test that auth commands are registered."""
        from ticktick_mcp.cli.commands import auth

        # Check that commands are defined as functions
        assert hasattr(auth, "status")
        assert hasattr(auth, "login")
        assert hasattr(auth, "logout")
        assert hasattr(auth, "finish")

    def test_logout_command_logic(self):
        """Test logout command logic with mocked file."""
        from ticktick_mcp.cli.commands.auth import app
        from typer.testing import CliRunner
        import tempfile
        import os

        runner = CliRunner()

        # Create a temp directory and change to it
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create token file
                token_file = os.path.join(tmpdir, ".ticktick_token.json")
                with open(token_file, "w") as f:
                    f.write('{"access_token": "test"}')

                result = runner.invoke(app, ["logout"])

                assert result.exit_code == 0
                assert not os.path.exists(token_file)
            finally:
                os.chdir(original_cwd)
