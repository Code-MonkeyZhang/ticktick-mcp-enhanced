"""
Configuration management for TickTick MCP.

This module handles client initialization, environment variables,
and global configuration settings.
"""

import os

from .ticktick_client import TickTickClient

ticktick = None


def initialize_client():
    """Initialize the TickTick client."""
    global ticktick
    try:
        ticktick = TickTickClient()

        return True
    except Exception as e:
        return False


def get_client():
    """Get the global TickTick client instance."""
    return ticktick


def ensure_client():
    """Ensure the client is initialized."""
    if not ticktick:
        initialize_client()
    return ticktick
