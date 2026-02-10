"""
TickTick configuration persistence module.

Provides persistent storage for OAuth configuration (account_type,
client_id, client_secret) so users don't need to set environment
variables every time.

Config file location: ~/.ticktick/config.json
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


def get_config_dir() -> Path:
    """Get the configuration directory path.

    Returns:
        Path to ~/.ticktick directory
    """
    home = Path.home()
    config_dir = home / ".ticktick"
    return config_dir


def get_config_file() -> Path:
    """Get the configuration file path.

    Returns:
        Path to ~/.ticktick/config.json
    """
    return get_config_dir() / "config.json"


def save_config(
    account_type: str,
    client_id: str,
    client_secret: str,
    redirect_uri: Optional[str] = None,
) -> None:
    """Save configuration to file.

    Args:
        account_type: Account type ("china" or "global")
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: OAuth redirect URI (optional, defaults to http://localhost:8000/callback)

    Raises:
        OSError: If unable to write config file
    """
    config_dir = get_config_dir()
    config_dir.mkdir(mode=0o700, exist_ok=True)

    config_file = get_config_file()

    config_data = {
        "account_type": account_type,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    if redirect_uri:
        config_data["redirect_uri"] = redirect_uri

    # Write with restricted permissions
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    # Set file permissions to owner read/write only
    config_file.chmod(0o600)


def load_config() -> Optional[Dict[str, Any]]:
    """Load configuration from file.

    Returns:
        Configuration dict with keys: account_type, client_id, client_secret
        Returns None if file doesn't exist or is invalid
    """
    config_file = get_config_file()

    if not config_file.exists():
        return None

    try:
        with open(config_file) as f:
            data = json.load(f)

        # Validate required fields
        required = ["account_type", "client_id", "client_secret"]
        if not all(key in data for key in required):
            return None

        return data
    except (json.JSONDecodeError, IOError, OSError):
        return None


def clear_config() -> None:
    """Remove configuration file.

    Does nothing if file doesn't exist.
    """
    config_file = get_config_file()

    if config_file.exists():
        config_file.unlink()


def is_configured() -> bool:
    """Check if configuration file exists and is valid.

    Returns:
        True if config exists with all required fields
    """
    config = load_config()
    return config is not None


def load_config_with_env_fallback() -> Optional[Dict[str, Any]]:
    """Load configuration with environment variable fallback.

    Priority order:
    1. Configuration file (~/.ticktick/config.json)
    2. Environment variables (TICKTICK_ACCOUNT_TYPE, TICKTICK_CLIENT_ID, TICKTICK_CLIENT_SECRET)

    Returns:
        Configuration dict or None if no configuration found
    """
    # Try config file first
    config = load_config()
    if config:
        return config

    # Fallback to environment variables
    account_type = os.getenv("TICKTICK_ACCOUNT_TYPE", "global").lower()
    client_id = os.getenv("TICKTICK_CLIENT_ID")
    client_secret = os.getenv("TICKTICK_CLIENT_SECRET")

    if client_id and client_secret:
        return {
            "account_type": account_type
            if account_type in ("china", "global")
            else "global",
            "client_id": client_id,
            "client_secret": client_secret,
        }

    return None
