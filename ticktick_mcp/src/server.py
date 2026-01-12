"""
Main MCP server for TickTick integration.
"""

import logging
from mcp.server.fastmcp import FastMCP

from .log import setup_logging
from .client_manager import initialize_client, get_client
from .tools.project_tools import register_project_tools
from .tools.task_tools import register_task_tools
from .tools.query_tools import register_query_tools
from .utils.logging_utils import log_interaction

logger = setup_logging("server")
mcp = FastMCP("ticktick")


def register_auth_tools(mcp_server: FastMCP):
    """Register authentication related tools."""

    @mcp_server.tool()
    @log_interaction
    async def ticktick_status() -> str:
        """
        Check the current connection status with TickTick.
        Returns whether the server is authenticated and ready to use.
        """
        client = get_client()
        if not client:
            return "Error: TickTick client not initialized."

        if client.auth.is_authenticated():
            return (
                f"✅ Connected to {client.auth.config['name']}. Ready to manage tasks."
            )
        else:
            return "❌ Not Authenticated. Please use the 'start_authentication' tool to log in."

    @mcp_server.tool()
    @log_interaction
    async def start_authentication() -> str:
        """
        Start the authentication process.
        Returns a URL that the user must visit to authorize the application.
        """
        client = get_client()
        if not client:
            return "Error: TickTick client not initialized."

        if not client.auth.is_configured():
            return "Error: Missing Client ID or Client Secret in configuration."

        try:
            client.auth.start_local_server()

            url = client.auth.get_auth_url()
            return f"""
Please open the following URL in your browser to authorize TickTick:

{url}

**Automatic Login:**
After you authorize, you will be automatically redirected to a local page confirming success.
You do NOT need to copy any code. Just close the window and return here.

**Manual Fallback:**
If the automatic login fails (e.g., page connection refused), please copy the 'code' parameter from the redirected URL and use the 'finish_authentication' tool manually.
"""
        except Exception as e:
            return f"Error generating auth URL: {str(e)}"

    @mcp_server.tool()
    @log_interaction
    async def finish_authentication(code: str) -> str:
        """
        Complete the authentication process using the code obtained from the browser.

        Args:
            code: The authorization code copied from the redirect URL.
        """
        client = get_client()
        if not client:
            return "Error: TickTick client not initialized."

        if client.auth.exchange_code(code):
            return "✅ Authentication successful! Token saved locally. You can now use all task tools."
        else:
            return "❌ Authentication failed. The code might be invalid or expired. Please try 'start_authentication' again."


def register_all_tools():
    """Register all MCP tools from modules."""
    register_auth_tools(mcp)

    register_project_tools(mcp)
    register_task_tools(mcp)
    register_query_tools(mcp)

    logger.info("All TickTick MCP tools registered successfully")


def main():
    """Main entry point for the MCP server."""
    initialize_client()
    register_all_tools()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
