"""
Tests for CLI context module.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestCLIContext:
    """Tests for CLIContext class."""

    def test_context_class_exists(self):
        """Test that CLIContext class exists."""
        from ticktick_mcp.cli.context import CLIContext

        assert CLIContext is not None

    def test_context_initialization(self):
        """Test CLIContext can be instantiated."""
        from ticktick_mcp.cli.context import CLIContext

        ctx = CLIContext()
        assert ctx is not None
        assert ctx._initialized is False
        assert ctx._client is None

    @patch("ticktick_mcp.client_manager.initialize_client")
    @patch("ticktick_mcp.client_manager.get_client")
    def test_ensure_authenticated_when_authenticated(self, mock_get_client, mock_init):
        """Test ensure_authenticated returns True when authenticated."""
        from ticktick_mcp.cli.context import CLIContext

        mock_client = MagicMock()
        mock_client.auth.is_authenticated.return_value = True
        mock_get_client.return_value = mock_client

        ctx = CLIContext()
        result = ctx.ensure_authenticated()

        assert result is True
        mock_init.assert_called_once()

    @patch("ticktick_mcp.client_manager.initialize_client")
    @patch("ticktick_mcp.client_manager.get_client")
    def test_ensure_authenticated_when_not_authenticated(
        self, mock_get_client, mock_init
    ):
        """Test ensure_authenticated returns False when not authenticated."""
        from ticktick_mcp.cli.context import CLIContext

        mock_client = MagicMock()
        mock_client.auth.is_authenticated.return_value = False
        mock_get_client.return_value = mock_client

        ctx = CLIContext()
        result = ctx.ensure_authenticated()

        assert result is False

    @patch("ticktick_mcp.client_manager.initialize_client")
    @patch("ticktick_mcp.client_manager.get_client")
    def test_get_client_returns_client(self, mock_get_client, mock_init):
        """Test get_client returns the TickTick client."""
        from ticktick_mcp.cli.context import CLIContext

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        ctx = CLIContext()
        client = ctx.get_client()

        assert client == mock_client

    @patch("ticktick_mcp.client_manager.initialize_client")
    @patch("ticktick_mcp.client_manager.get_client")
    def test_get_client_raises_when_none(self, mock_get_client, mock_init):
        """Test get_client raises RuntimeError when client is None."""
        from ticktick_mcp.cli.context import CLIContext

        mock_get_client.return_value = None

        ctx = CLIContext()

        with pytest.raises(RuntimeError, match="Client not initialized"):
            ctx.get_client(raise_error=True)

    def test_require_auth_without_authentication(self):
        """Test require_auth returns False and prints error when not authenticated."""
        from ticktick_mcp.cli.context import CLIContext

        ctx = CLIContext()

        # Mock the console.print to avoid actual output
        with patch("ticktick_mcp.cli.console.console.print"):
            with patch(
                "ticktick_mcp.cli.context.CLIContext.ensure_authenticated",
                return_value=False,
            ):
                result = ctx.require_auth()

        assert result is False

    @patch("ticktick_mcp.client_manager.initialize_client")
    @patch("ticktick_mcp.client_manager.get_client")
    def test_require_auth_with_authentication(self, mock_get_client, mock_init):
        """Test require_auth returns True when authenticated."""
        from ticktick_mcp.cli.context import CLIContext

        mock_client = MagicMock()
        mock_client.auth.is_authenticated.return_value = True
        mock_get_client.return_value = mock_client

        ctx = CLIContext()
        result = ctx.require_auth()

        assert result is True
