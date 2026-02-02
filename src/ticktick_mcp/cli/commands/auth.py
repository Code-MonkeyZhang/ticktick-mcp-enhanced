"""
Authentication commands for TickTick CLI.

Enhanced with interactive configuration support.
"""

import typer
from typing import Optional

from ..context import CLIContext
from ..console import print_success, print_error, print_info, console


app = typer.Typer(
    help="Authentication commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _prompt_for_config():
    """Prompt user for OAuth configuration.

    Returns:
        Tuple of (account_type, client_id, client_secret, redirect_uri) or None if cancelled
    """
    console.print("\n[bold cyan]TickTick Configuration[/bold cyan]")
    console.print(
        "To use TickTick CLI, you need to configure OAuth credentials.\n"
        "Get your credentials at: https://platform.dida365.com/oauth/apps\n"
    )

    # Prompt for account type
    console.print("\n[bold]Account Type:[/bold]")
    console.print("  1. China (Dida365/滴答清单)")
    console.print("  2. Global (TickTick)")

    account_choice = typer.prompt(
        "\nSelect account type",
        type=int,
        default=1,
        show_default=False,
    )

    if account_choice == 1:
        account_type = "china"
    elif account_choice == 2:
        account_type = "global"
    else:
        print_error("Invalid choice. Please enter 1 or 2.")
        return None

    # Prompt for client credentials
    client_id = typer.prompt("\nClient ID", type=str)
    if not client_id.strip():
        print_error("Client ID cannot be empty.")
        return None

    client_secret = typer.prompt("Client Secret", type=str)
    if not client_secret.strip():
        print_error("Client Secret cannot be empty.")
        return None

    # Prompt for redirect URI (optional)
    console.print("\n[bold]Redirect URI:[/bold]")
    console.print(
        "  This must match the callback URL you registered in the OAuth app.\n"
        "  Default: http://localhost:8000/callback"
    )
    redirect_uri = typer.prompt(
        "\nRedirect URI",
        type=str,
        default="http://localhost:8000/callback",
    )

    # Allow empty to use default
    if not redirect_uri.strip():
        redirect_uri = "http://localhost:8000/callback"

    return account_type, client_id, client_secret, redirect_uri


@app.command()
def status():
    """Check current authentication status."""
    from ...config import is_configured

    ctx = CLIContext()

    if not is_configured():
        print_error("Not configured")
        print_info("Run 'ticktick auth login' to configure")
        return

    if ctx.ensure_authenticated():
        client = ctx.get_client()
        account_name = client.auth.config.get("name", "TickTick")
        print_success(f"Authenticated with {account_name}")
    else:
        print_error("Not authenticated")
        print_info("Run 'ticktick auth login' to authenticate")


@app.command()
def login():
    """Start the OAuth authentication flow.

    Prompts for configuration if not already set up.
    """
    from ...config import is_configured

    ctx = CLIContext()
    client = ctx.get_client()

    # Check if configured
    if not client.auth.is_configured():
        console.print("\n[yellow]OAuth credentials not configured.[/yellow]")
        result = _prompt_for_config()

        if result is None:
            print_error("Configuration cancelled.")
            raise typer.Exit(1)

        account_type, client_id, client_secret, redirect_uri = result

        # Save configuration
        try:
            client.auth.save_config(
                account_type, client_id, client_secret, redirect_uri
            )
            print_success("Configuration saved!")
        except Exception as e:
            print_error(f"Failed to save configuration: {e}")
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
    """Clear authentication token and configuration."""
    from ...config import is_configured
    from pathlib import Path

    ctx = CLIContext()
    client = ctx.get_client(raise_error=False)

    # Clear token file
    token_file = Path.cwd() / ".ticktick_token.json"
    if token_file.exists():
        token_file.unlink()

    # Clear config if client is available
    if client:
        client.auth.clear_config()

    print_success("Logged out successfully")


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
