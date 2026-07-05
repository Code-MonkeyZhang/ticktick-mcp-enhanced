"""
Main MCP server for TickTick integration.
"""

from mcp.server.fastmcp import FastMCP

from .log import setup_logging
from .client_manager import initialize_client, get_client
from .tools.project_tools import register_project_tools
from .tools.task_tools import register_task_tools
from .tools.query_tools import register_query_tools
from .tools.habit_tools import register_habit_tools
from .tools.prompts import load_prompt
from .utils.logging_utils import log_interaction

logger = setup_logging("server")
mcp = FastMCP("ticktick")


def register_auth_tools(mcp_server: FastMCP):
    """Register authentication related tools."""

    @mcp_server.tool(description=load_prompt("ticktick_status"))
    @log_interaction
    async def ticktick_status() -> str:
        client = get_client()
        if not client:
            return "Error: TickTick client not initialized."

        if not client.auth.is_configured():
            return "❌ Not configured. Please use the 'login' tool to provide your TickTick OAuth credentials."

        if client.auth.is_authenticated():
            return (
                f"✅ Connected to {client.auth.config['name']}. Ready to manage tasks."
            )
        else:
            return "❌ Configured but not authenticated. Please use the 'login' tool to log in."

    @mcp_server.tool(description=load_prompt("login"))
    @log_interaction
    async def login(
        client_id: str,
        client_secret: str,
        account_type: str = "china",
        redirect_uri: str = "http://localhost:8000/callback",
    ) -> str:
        client = get_client()
        if not client:
            return "Error: TickTick client not initialized."

        if not client.auth.configure(
            client_id, client_secret, account_type, redirect_uri
        ):
            return (
                "❌ Invalid account_type. Use 'china' for Dida365 "
                "or 'global' for TickTick international."
            )

        result = client.auth.start_oauth_flow()

        if result == "success":
            return "✅ Login successful! You can now manage your tasks."
        elif result.startswith("error:"):
            detail = result[len("error:"):]
            return f"❌ Authorization failed: {detail}. Please try 'login' again."
        else:
            url = result[len("timeout:"):]
            return (
                f"⏰ Login timed out. If the browser did not open automatically, "
                f"please visit this URL manually:\n{url}"
            )


def register_all_tools():
    """Register all MCP tools from modules."""
    register_auth_tools(mcp)

    register_project_tools(mcp)
    register_task_tools(mcp)
    register_query_tools(mcp)
    register_habit_tools(mcp)

    logger.info("All TickTick MCP tools registered successfully")


def main():
    """Main entry point for the MCP server."""
    initialize_client()
    register_all_tools()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
