"""
Tests for configuration persistence module.

TDD Approach:
1. These tests are written BEFORE the config module exists
2. They define the expected behavior and API
3. Run with pytest to verify RED state before implementation
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner


class TestConfigPaths:
    """Tests for configuration file path handling."""

    def test_config_dir_returns_path(self):
        """Test that get_config_dir returns a Path object."""
        from ticktick_mcp.config import get_config_dir

        result = get_config_dir()
        assert isinstance(result, Path)

    def test_config_dir_is_ticktick_hidden(self):
        """Test that config dir is ~/.ticktick."""
        from ticktick_mcp.config import get_config_dir

        result = get_config_dir()
        # Should be a hidden .ticktick directory
        assert result.name == ".ticktick"

    def test_config_file_returns_path(self):
        """Test that get_config_file returns a Path object."""
        from ticktick_mcp.config import get_config_file

        result = get_config_file()
        assert isinstance(result, Path)
        assert result.name == "config.json"


class TestConfigReadWrite:
    """Tests for configuration read/write operations."""

    def test_save_config_creates_file(self, tmp_path):
        """Test that save_config creates a config file."""
        from ticktick_mcp.config import save_config

        # Patch config dir to use temp path
        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            save_config(
                account_type="china",
                client_id="test_client_id",
                client_secret="test_secret",
            )

            config_file = tmp_path / "config.json"
            assert config_file.exists()

    def test_save_config_stores_correct_data(self, tmp_path):
        """Test that save_config stores data in correct format."""
        from ticktick_mcp.config import save_config

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            save_config(
                account_type="china",
                client_id="d7xCKF19RdY3tQpb8g",
                client_secret="Q6fPZ7zaL2J8mdRtvPnJIJ820Qwz68Fq",
            )

            config_file = tmp_path / "config.json"
            with open(config_file) as f:
                data = json.load(f)

            assert data["account_type"] == "china"
            assert data["client_id"] == "d7xCKF19RdY3tQpb8g"
            assert data["client_secret"] == "Q6fPZ7zaL2J8mdRtvPnJIJ820Qwz68Fq"

    def test_load_config_returns_none_when_missing(self, tmp_path):
        """Test that load_config returns None when file doesn't exist."""
        from ticktick_mcp.config import load_config

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            result = load_config()
            assert result is None

    def test_load_config_returns_dict_when_exists(self, tmp_path):
        """Test that load_config returns config dict when file exists."""
        from ticktick_mcp.config import save_config, load_config

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # First save some config
            save_config(
                account_type="global", client_id="test_id", client_secret="test_secret"
            )

            # Then load it
            result = load_config()

            assert result is not None
            assert result["account_type"] == "global"
            assert result["client_id"] == "test_id"
            assert result["client_secret"] == "test_secret"

    def test_load_config_handles_invalid_json(self, tmp_path):
        """Test that load_config handles invalid JSON gracefully."""
        from ticktick_mcp.config import load_config

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # Create invalid JSON file
            config_file = tmp_path / "config.json"
            config_file.write_text("{ invalid json")

            result = load_config()
            assert result is None

    def test_clear_config_removes_file(self, tmp_path):
        """Test that clear_config removes the config file."""
        from ticktick_mcp.config import save_config, clear_config

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # First create config
            save_config(
                account_type="china", client_id="test_id", client_secret="test_secret"
            )

            config_file = tmp_path / "config.json"
            assert config_file.exists()

            # Then clear it
            clear_config()

            assert not config_file.exists()

    def test_clear_config_is_idempotent(self, tmp_path):
        """Test that clear_config doesn't error when file doesn't exist."""
        from ticktick_mcp.config import clear_config

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # Should not raise even if file doesn't exist
            clear_config()
            clear_config()  # Call again


class TestConfigIsConfigured:
    """Tests for is_configured helper."""

    def test_is_configured_returns_false_when_missing(self, tmp_path):
        """Test that is_configured returns False when config is missing."""
        from ticktick_mcp.config import is_configured

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            assert is_configured() is False

    def test_is_configured_returns_false_when_invalid(self, tmp_path):
        """Test that is_configured returns False when config is invalid."""
        from ticktick_mcp.config import is_configured

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # Create incomplete config
            config_file = tmp_path / "config.json"
            config_file.write_text('{"account_type": "china"}')

            assert is_configured() is False

    def test_is_configured_returns_true_when_valid(self, tmp_path):
        """Test that is_configured returns True when config is valid."""
        from ticktick_mcp.config import save_config, is_configured

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            save_config(
                account_type="global", client_id="test_id", client_secret="test_secret"
            )

            assert is_configured() is True


class TestConfigIntegration:
    """Integration tests for config with environment variables."""

    def test_load_fallback_to_env_when_config_missing(self, tmp_path, monkeypatch):
        """Test that when config is missing, environment variables are used."""
        from ticktick_mcp.config import load_config_with_env_fallback

        monkeypatch.setenv("TICKTICK_ACCOUNT_TYPE", "china")
        monkeypatch.setenv("TICKTICK_CLIENT_ID", "env_id")
        monkeypatch.setenv("TICKTICK_CLIENT_SECRET", "env_secret")

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            result = load_config_with_env_fallback()

            assert result is not None
            assert result["account_type"] == "china"
            assert result["client_id"] == "env_id"
            assert result["client_secret"] == "env_secret"

    def test_load_config_takes_precedence_over_env(self, tmp_path, monkeypatch):
        """Test that config file takes precedence over environment variables."""
        from ticktick_mcp.config import save_config, load_config_with_env_fallback

        # Set env vars
        monkeypatch.setenv("TICKTICK_ACCOUNT_TYPE", "global")
        monkeypatch.setenv("TICKTICK_CLIENT_ID", "env_id")
        monkeypatch.setenv("TICKTICK_CLIENT_SECRET", "env_secret")

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            # Save config with different values
            save_config(
                account_type="china", client_id="file_id", client_secret="file_secret"
            )

            result = load_config_with_env_fallback()

            # Config file values should take precedence
            assert result["account_type"] == "china"
            assert result["client_id"] == "file_id"
            assert result["client_secret"] == "file_secret"

    def test_load_with_env_fallback_returns_none_when_all_missing(self, tmp_path):
        """Test that load_with_env_fallback returns None when nothing is configured."""
        from ticktick_mcp.config import load_config_with_env_fallback

        # Clear all env vars
        for key in [
            "TICKTICK_ACCOUNT_TYPE",
            "TICKTICK_CLIENT_ID",
            "TICKTICK_CLIENT_SECRET",
        ]:
            import os

            os.environ.pop(key, None)

        with patch("ticktick_mcp.config.get_config_dir", return_value=tmp_path):
            result = load_config_with_env_fallback()
            assert result is None
