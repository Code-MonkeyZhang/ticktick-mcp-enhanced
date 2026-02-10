"""
CLI context management for TickTick.

Provides CLIContext class for managing authentication state
and client initialization in CLI commands.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..ticktick_client import TickTickClient


class CLIContext:
    """Context manager for CLI operations.

    Manages authentication state and provides access to TickTick client.
    """

    def __init__(self) -> None:
        """Initialize CLI context."""
        self._client: Optional["TickTickClient"] = None
        self._initialized: bool = False

    def _ensure_client_initialized(self) -> bool:
        """Ensure the TickTick client is initialized.

        Returns:
            True if client is initialized, False otherwise
        """
        if self._initialized:
            return True

        from ..client_manager import initialize_client, get_client

        try:
            initialize_client()
            self._client = get_client()
            self._initialized = True
            return True
        except Exception:
            return False

    def ensure_authenticated(self) -> bool:
        """Check if user is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        if not self._ensure_client_initialized():
            return False

        if self._client and self._client.auth.is_authenticated():
            return True

        return False

    def get_client(self, raise_error: bool = False) -> Optional["TickTickClient"]:
        """Get the TickTick client instance.

        Args:
            raise_error: If True, raise RuntimeError when client is None

        Returns:
            TickTickClient instance or None

        Raises:
            RuntimeError: If raise_error is True and client is None
        """
        self._ensure_client_initialized()

        if self._client is None and raise_error:
            raise RuntimeError("Client not initialized")

        return self._client

    def require_auth(self) -> bool:
        """Ensure user is authenticated, print error if not.

        Returns:
            True if authenticated, False otherwise
        """
        if not self.ensure_authenticated():
            from .console import print_error

            print_error("Not authenticated. Please run 'ticktick auth login' first.")
            return False

        return True
