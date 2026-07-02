"""
Configuration management for TickTick MCP.

This module handles client initialization and global configuration settings.
"""

from .ticktick_client import TickTickClient

ticktick = None


def initialize_client():
    """Initialize the TickTick client."""
    global ticktick
    try:
        ticktick = TickTickClient()

        return True
    except Exception:
        return False


def get_client():
    """Get the global TickTick client instance."""
    return ticktick


def ensure_client():
    """Ensure the client is initialized."""
    if not ticktick:
        initialize_client()
    return ticktick
