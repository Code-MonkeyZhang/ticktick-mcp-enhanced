"""
Tests for TickTickAuth with configuration file support.

TDD Approach: Tests written BEFORE modifying TickTickAuth
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestTickTickAuthConfig:
    """Tests for TickTickAuth configuration loading."""

    def test_auth_prefers_config_file_over_env(self, tmp_path, monkeypatch):
        """Test that config file takes precedence over environment variables."""
        from ticktick_mcp.config import save_config
        from ticktick_mcp.auth import TickTickAuth

        # Set env vars
        monkeypatch.setenv("TICKTICK_ACCOUNT_TYPE", "global")
        monkeypatch.setenv("TICKTICK_CLIENT_ID", "env_id")
        monkeypatch.setenv("TICKTICK_CLIENT_SECRET", "env_secret")

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # Save config with different values
            save_config(
                account_type="china", client_id="file_id", client_secret="file_secret"
            )

            # Create auth instance
            auth = TickTickAuth()

            # Config file values should take precedence
            assert auth.account_type == "china"
            assert auth.client_id == "file_id"
            assert auth.client_secret == "file_secret"

    def test_auth_uses_env_when_no_config(self, tmp_path, monkeypatch):
        """Test that environment variables are used when config file doesn't exist."""
        from ticktick_mcp.auth import TickTickAuth

        # Clear any existing config
        monkeypatch.setenv("TICKTICK_ACCOUNT_TYPE", "china")
        monkeypatch.setenv("TICKTICK_CLIENT_ID", "env_id")
        monkeypatch.setenv("TICKTICK_CLIENT_SECRET", "env_secret")

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            auth = TickTickAuth()

            assert auth.account_type == "china"
            assert auth.client_id == "env_id"
            assert auth.client_secret == "env_secret"

    def test_auth_uses_default_when_nothing_configured(self, tmp_path):
        """Test default values when nothing is configured."""
        from ticktick_mcp.auth import TickTickAuth

        # Clear all env vars and ensure no config file
        with patch.dict("os.environ", {}, clear=True):
            with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
                auth = TickTickAuth()

                assert auth.account_type == "global"  # Default
                assert auth.client_id is None
                assert auth.client_secret is None

    def test_auth_is_configured_with_config_file(self, tmp_path, monkeypatch):
        """Test is_configured returns True when config file exists."""
        from ticktick_mcp.config import save_config
        from ticktick_mcp.auth import TickTickAuth

        # Clear env vars
        for key in ["TICKTICK_CLIENT_ID", "TICKTICK_CLIENT_SECRET"]:
            monkeypatch.delenv(key, raising=False)

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            save_config(
                account_type="global", client_id="test_id", client_secret="test_secret"
            )

            auth = TickTickAuth()
            assert auth.is_configured() is True

    def test_auth_is_configured_with_env_vars(self, tmp_path, monkeypatch):
        """Test is_configured returns True when env vars are set."""
        from ticktick_mcp.auth import TickTickAuth

        monkeypatch.setenv("TICKTICK_CLIENT_ID", "test_id")
        monkeypatch.setenv("TICKTICK_CLIENT_SECRET", "test_secret")

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            auth = TickTickAuth()
            assert auth.is_configured() is True

    def test_auth_is_configured_returns_false_when_unconfigured(self, tmp_path):
        """Test is_configured returns False when nothing is configured."""
        from ticktick_mcp.auth import TickTickAuth

        with patch.dict("os.environ", {}, clear=True):
            with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
                auth = TickTickAuth()
                assert auth.is_configured() is False


class TestTickTickAuthSaveConfig:
    """Tests for TickTickAuth.save_config method."""

    def test_save_config_creates_config_file(self, tmp_path):
        """Test that auth.save_config creates a config file."""
        from ticktick_mcp.auth import TickTickAuth

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            auth = TickTickAuth()
            auth.save_config(
                account_type="china", client_id="new_id", client_secret="new_secret"
            )

            # Verify config file was created
            config_file = tmp_path / "config.json"
            assert config_file.exists()

    def test_save_config_updates_instance(self, tmp_path):
        """Test that save_config updates the auth instance."""
        from ticktick_mcp.auth import TickTickAuth

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            auth = TickTickAuth()
            auth.save_config(
                account_type="china", client_id="new_id", client_secret="new_secret"
            )

            assert auth.account_type == "china"
            assert auth.client_id == "new_id"
            assert auth.client_secret == "new_secret"


class TestTickTickAuthClearConfig:
    """Tests for TickTickAuth.clear_config method."""

    def test_clear_config_removes_file(self, tmp_path):
        """Test that clear_config removes the config file."""
        from ticktick_mcp.config import save_config
        from ticktick_mcp.auth import TickTickAuth

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # First create config
            save_config(
                account_type="global", client_id="test_id", client_secret="test_secret"
            )

            auth = TickTickAuth()
            assert auth.is_configured() is True

            # Clear config
            auth.clear_config()

            assert auth.is_configured() is False
