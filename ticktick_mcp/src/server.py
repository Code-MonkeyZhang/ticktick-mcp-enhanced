"""
Main MCP server for TickTick integration.

This is the core server that initializes the FastMCP server and registers
all the TickTick tools from the various modules.
"""

import logging
from mcp.server.fastmcp import FastMCP

from .log import setup_logging
from .config import initialize_client, get_client
from .tools.project_tools import register_project_tools
from .tools.task_tools import register_task_tools
from .tools.query_tools import register_query_tools
from .utils.logging_utils import log_interaction

# Initialize logging
logger = setup_logging("server")

# Create FastMCP server
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
            return f"✅ Connected to {client.auth.config['name']}. Ready to manage tasks."
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
            # Start local listener for callback
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
    # Register auth tools first
    register_auth_tools(mcp)
    
    # Register business tools (project, task, query)
    # These modules should import 'mcp' from here or pass it in
    # The existing code structure passes 'mcp' instance, so we keep that pattern.
    # Note: We need to import the registration functions if they aren't already imported.
    # But wait, looking at the previous file content, they were imported from .tools
    # Let's verify the imports in the previous file content.
    # Yes: from .tools import register_project_tools, etc.
    # But I see in my new imports I made them explicit.
    
    # Re-import just to be safe if structure is different
    from .tools.project_tools import register_project_tools
    from .tools.task_tools import register_task_tools
    from .tools.query_tools import register_query_tools
    
    register_project_tools(mcp)
    register_task_tools(mcp)
    register_query_tools(mcp)
    
    logger.info("All TickTick MCP tools registered successfully")


def main():
    """Main entry point for the MCP server."""
    # Initialize the TickTick client wrapper
    # This will succeed even if no token is present (Server First philosophy)
    initialize_client()
    
    # Register all tools
    register_all_tools()
    
    # Run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()