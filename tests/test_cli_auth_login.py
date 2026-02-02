"""
Tests for enhanced auth login with interactive configuration.

TDD Approach: Tests written BEFORE modifying login command
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call


class TestAuthLoginInteractive:
    """Tests for interactive configuration during login."""

    @patch("ticktick_mcp.cli.commands.auth.typer.prompt")
    def test_login_prompts_for_config_when_not_configured(self, mock_prompt, tmp_path):
        """Test that login prompts for configuration when not configured."""
        from ticktick_mcp.cli.commands.auth import login
        import typer

        # Setup mock to return config values (account, client_id, client_secret, redirect_uri)
        mock_prompt.side_effect = [
            1,
            "test_id",
            "test_secret",
            "http://localhost:8000/callback",
        ]

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            with patch("ticktick_mcp.cli.commands.auth.CLIContext") as mock_ctx:
                mock_client = MagicMock()
                mock_client.auth.is_configured.return_value = False
                mock_client.auth.is_authenticated.return_value = True
                mock_ctx.return_value.get_client.return_value = mock_client

                # Call login - should raise Exit(0) when authenticated
                with pytest.raises(typer.Exit) as exc_info:
                    login()

                assert exc_info.value.exit_code == 0
                # Should prompt 4 times: account choice, client_id, client_secret, redirect_uri
                assert mock_prompt.call_count == 4
                # Should save config
                mock_client.auth.save_config.assert_called_once_with(
                    "china", "test_id", "test_secret", "http://localhost:8000/callback"
                )

    @patch("ticktick_mcp.config.load_config")
    @patch("ticktick_mcp.cli.commands.auth.typer.prompt")
    def test_login_saves_config_after_prompt(
        self, mock_prompt, mock_load_config, tmp_path
    ):
        """Test that login saves configuration after prompting."""
        from ticktick_mcp.cli.commands.auth import login
        import typer

        # Setup mock to return config values (global account)
        mock_prompt.side_effect = [
            2,
            "test_id",
            "test_secret",
            "http://localhost:8000/callback",
        ]

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            with patch("ticktick_mcp.cli.commands.auth.CLIContext") as mock_ctx:
                mock_client = MagicMock()
                mock_client.auth.is_configured.return_value = False
                mock_client.auth.is_authenticated.return_value = True
                mock_ctx.return_value.get_client.return_value = mock_client

                # Mock load_config to return saved values
                mock_load_config.return_value = {
                    "account_type": "global",
                    "client_id": "test_id",
                    "client_secret": "test_secret",
                }

                # Call login - should raise Exit(0) when authenticated
                with pytest.raises(typer.Exit) as exc_info:
                    login()

                assert exc_info.value.exit_code == 0

                # Verify save_config was called with redirect_uri
                mock_client.auth.save_config.assert_called_once_with(
                    "global", "test_id", "test_secret", "http://localhost:8000/callback"
                )

    def test_login_skips_prompt_when_configured(self, tmp_path):
        """Test that login skips prompts when already configured."""
        from ticktick_mcp.cli.commands.auth import login
        from ticktick_mcp.config import save_config
        import typer

        # Save config first
        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            save_config(
                account_type="china",
                client_id="test_id",
                client_secret="test_secret",
            )

            with patch("ticktick_mcp.cli.commands.auth.CLIContext") as mock_ctx:
                mock_client = MagicMock()
                mock_client.auth.is_configured.return_value = True
                mock_client.auth.is_authenticated.return_value = True
                mock_client.auth.get_auth_url.return_value = "http://test.url"
                mock_ctx.return_value.get_client.return_value = mock_client

                # Call login - should raise Exit(0) when authenticated
                with pytest.raises(typer.Exit) as exc_info:
                    login()

                assert exc_info.value.exit_code == 0
                # Should not call save_config since already configured
                mock_client.auth.save_config.assert_not_called()

    @patch("ticktick_mcp.cli.commands.auth.typer.prompt")
    def test_login_handles_invalid_account_choice(self, mock_prompt, tmp_path):
        """Test that login handles invalid account choice."""
        from ticktick_mcp.cli.commands.auth import login
        import typer

        # Setup mock to return invalid choice
        mock_prompt.side_effect = [
            99,
            "test_id",
            "test_secret",
            "http://localhost:8000/callback",
        ]

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            with patch("ticktick_mcp.cli.commands.auth.CLIContext") as mock_ctx:
                mock_client = MagicMock()
                mock_client.auth.is_configured.return_value = False
                mock_ctx.return_value.get_client.return_value = mock_client

                # Call login - should exit with code 1 due to invalid choice
                with pytest.raises(typer.Exit) as exc_info:
                    login()

                assert exc_info.value.exit_code == 1


class TestAuthLogoutEnhanced:
    """Tests for enhanced logout that clears config."""

    def test_logout_clears_config(self, tmp_path):
        """Test that logout clears config."""
        from ticktick_mcp.cli.commands.auth import logout
        from ticktick_mcp.config import save_config, is_configured

        # Create config first
        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            save_config(
                account_type="global",
                client_id="test_id",
                client_secret="test_secret",
            )
            assert is_configured() is True

            with patch("ticktick_mcp.cli.commands.auth.CLIContext") as mock_ctx:
                mock_client = MagicMock()
                mock_ctx.return_value.get_client.return_value = mock_client
                mock_ctx.return_value.get_client.return_value = mock_client

                # Call logout
                logout()

                # Should call clear_config
                mock_client.auth.clear_config.assert_called_once()


class TestAuthStatusEnhanced:
    """Tests for enhanced auth status showing config state."""

    def test_status_shows_not_configured(self, tmp_path):
        """Test that status shows when not configured."""
        from ticktick_mcp.cli.commands.auth import status
        from ticktick_mcp.config import is_configured

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            assert is_configured() is False

            with patch("ticktick_mcp.cli.commands.auth.print_success") as mock_success:
                with patch("ticktick_mcp.cli.commands.auth.print_error") as mock_error:
                    with patch(
                        "ticktick_mcp.cli.commands.auth.print_info"
                    ) as mock_info:
                        with patch("ticktick_mcp.cli.commands.auth.CLIContext"):
                            status()

                            # Should show not configured error
                            mock_error.assert_called()
                            error_msg = mock_error.call_args[0][0]
                            assert "Not configured" in error_msg
