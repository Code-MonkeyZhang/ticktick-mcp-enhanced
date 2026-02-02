"""
Authentication commands for TickTick CLI.
"""

import typer
from typing import Optional

from ..context import CLIContext
from ..console import print_success, print_error, print_info, console


app = typer.Typer(help="Authentication commands")


@app.command()
def status():
    """Check current authentication status."""
    ctx = CLIContext()

    if ctx.ensure_authenticated():
        client = ctx.get_client()
        account_name = client.auth.config.get("name", "TickTick")
        print_success(f"Authenticated with {account_name}")
    else:
        print_error("Not authenticated")
        print_info("Run 'ticktick auth login' to authenticate")


@app.command()
def login():
    """Start the OAuth authentication flow."""
    ctx = CLIContext()
    client = ctx.get_client()

    if not client.auth.is_configured():
        print_error(
            "Missing TICKTICK_CLIENT_ID or TICKTICK_CLIENT_SECRET environment variables"
        )
        raise typer.Exit(1)

    # Start the local server to receive callback
    client.auth.start_local_server()

    # Get the auth URL
    url = client.auth.get_auth_url()

    console.print("\n[bold cyan]Login to TickTick[/bold cyan]\n")
    console.print("Please open the following URL in your browser:\n")
    console.print(f"[link]{url}[/link]\n", soft_wrap=True)
    console.print(
        "After authorization, you will be redirected automatically. "
        "If the automatic redirect fails, copy the 'code' parameter from the URL "
        "and run 'ticktick auth finish <code>'.\n"
    )

    # Wait for token...
    print_info("Waiting for authentication...")

    import time

    max_wait = 120  # 2 minutes
    start = time.time()

    while time.time() - start < max_wait:
        if client.auth.is_authenticated():
            print_success("Authentication successful!")
            raise typer.Exit(0)
        time.sleep(1)

    print_error("Authentication timeout")
    raise typer.Exit(1)


@app.command()
def logout():
    """Clear authentication token."""
    import os
    from pathlib import Path

    token_file = Path.cwd() / ".ticktick_token.json"

    if token_file.exists():
        token_file.unlink()
        print_success("Logged out successfully")
    else:
        print_info("No authentication token found")


@app.command()
def finish(code: str):
    """Complete authentication with a code.

    Use this if the automatic redirect fails.
    """
    ctx = CLIContext()
    client = ctx.get_client()

    if client.auth.exchange_code(code):
        print_success("Authentication successful!")
    else:
        print_error("Authentication failed. The code may be invalid or expired.")
        raise typer.Exit(1)
