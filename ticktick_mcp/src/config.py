"""
Configuration management for TickTick MCP.

This module handles client initialization, environment variables,
and global configuration settings.
"""

import os
import logging

from .ticktick_client import TickTickClient

logger = logging.getLogger(__name__)

ticktick = None


def initialize_client():
    """Initialize the TickTick client."""
    global ticktick
    try:
        ticktick = TickTickClient()
        logger.info("TickTick client wrapper initialized")

        return True
    except Exception as e:
        logger.error(f"Failed to initialize TickTick client wrapper: {e}")
        return False


def get_client():
    """Get the global TickTick client instance."""
    return ticktick


def ensure_client():
    """Ensure the client is initialized."""
    if not ticktick:
        initialize_client()
    return ticktick
