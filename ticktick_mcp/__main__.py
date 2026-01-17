#!/usr/bin/env python3
"""
Main entry point for TickTick MCP server.
"""

import sys
import os

# 彻底静音：将 stderr 重定向到 devnull
# 这样可以消除 FastMCP 的 Banner 以及所有第三方库的日志干扰
sys.stderr = open(os.devnull, 'w')

import logging
import argparse
from .src.server import main as server_main


def main():
    """Entry point for the package."""
    parser = argparse.ArgumentParser(description="TickTick MCP Server")
    parser.add_argument(
        "command", nargs="?", default="run", choices=["run"], help="Command to run"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    try:
        server_main()
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
