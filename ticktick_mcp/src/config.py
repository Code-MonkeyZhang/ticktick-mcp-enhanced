"""
Configuration management for TickTick MCP.

This module handles client initialization, environment variables,
and global configuration settings.
"""

import os
import logging
from dotenv import load_dotenv

from .ticktick_client import TickTickClient

# Set up logging
logger = logging.getLogger(__name__)

# Global client instance
ticktick = None


def initialize_client():
    """Initialize the TickTick client."""
    global ticktick
    try:
        # Load environment variables (support both .env and system env)
        load_dotenv()
        
        # We no longer fail if token is missing. 
        # The client will be initialized in a "disconnected" state if needed,
        # or the auth tools will be used to establish connection.
        
        # Initialize the client (it handles its own auth check internally now)
        ticktick = TickTickClient()
        logger.info("TickTick client wrapper initialized")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize TickTick client wrapper: {e}")
        # Even if initialization fails, we don't want to crash the MCP server
        # We just won't have a working client
        return False


def get_client():
    """Get the global TickTick client instance."""
    return ticktick


def ensure_client():
    """Ensure the client is initialized."""
    if not ticktick:
        initialize_client()
    return ticktick