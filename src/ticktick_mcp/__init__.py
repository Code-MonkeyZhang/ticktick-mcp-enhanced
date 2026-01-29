# TickTick MCP Server


def main():
    """MCP Server 入口"""
    from .server import register_all_tools, mcp

    register_all_tools()
    mcp.run()
