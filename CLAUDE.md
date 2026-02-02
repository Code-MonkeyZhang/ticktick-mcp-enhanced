# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TickTick MCP Server is a Python-based Model Context Protocol (MCP) server that enables LLMs to manage TickTick/Dida365 (滴答清单) to-do lists through natural language commands.

- **Language**: Python 3.10+
- **Package Manager**: uv (Astral)
- **Entry Point**: `ticktick-mcp` command (defined in `pyproject.toml`)
- **Transport**: stdio (standard input/output)

## Common Commands

```bash
# Install dependencies and package in editable mode
uv pip install -e .

# Run the MCP server
uv run ticktick-mcp

# Build distribution package
uv run python -m build
```

## Architecture

### Entry Point Flow

```
ticktick-mcp (CLI)
    └── src/ticktick_mcp/__init__.py:main()
        └── src/ticktick_mcp/server.py:main()
            ├── initialize_client()     # Sets up TickTickClient singleton
            ├── register_all_tools()    # Registers all MCP tools
            └── mcp.run(transport="stdio")
```

### Core Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **MCP Server** | `server.py` | FastMCP instance, tool registration, main loop |
| **Auth Manager** | `auth.py` | OAuth 2.0 flow, token storage/loading, local callback server on port 8000 |
| **API Client** | `ticktick_client.py` | HTTP requests to TickTick API |
| **Client Manager** | `client_manager.py` | Global singleton client instance (`ticktick` variable) |
| **Logging** | `log.py` | Session-based file logging (strictly file-only, no stdout) |

### Tool Organization

Tools are organized by category in `src/ticktick_mcp/tools/`:

- **project_tools.py**: Project CRUD operations
- **task_tools.py**: Task CRUD operations (all support batch processing)
- **query_tools.py**: Task filtering and search

### Key Design Patterns

1. **Batch Operations**: All task operations support single dict or list of dicts input
2. **Priority Values**: 0 (none), 1 (low), 3 (medium), 5 (high)
3. **Date Handling**: ISO 8601 with timezone offsets (e.g., `2025-12-16T16:00:00+08:00`)
4. **Timezone**: IANA timezone names (e.g., "Asia/Shanghai")

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TICKTICK_ACCOUNT_TYPE` | `"china"` or `"global"` | `"global"` |
| `TICKTICK_CLIENT_ID` | OAuth client ID | - |
| `TICKTICK_CLIENT_SECRET` | OAuth client secret | - |
| `TICKTICK_REDIRECT_URI` | Callback URL | `http://localhost:8000/callback` |
| `TICKTICK_DISPLAY_TIMEZONE` | Display timezone | `"Local"` |
| `MCP_LOG_ENABLE` | Enable file logging (`"true"` or `"false"`) | `"false"` |

## Important Notes

- **Token Storage**: `.ticktick_token.json` in project root (gitignored)
- **Logging**: When enabled, logs are written to `logs/session_YYYYMMDD_HHMMSS.log` - never to stdout/stderr to avoid interfering with MCP protocol
- **API Endpoints**: Different for china vs global (see `VERSION_CONFIGS` in `auth.py`)
- **Authentication Flow**: OAuth 2.0 with local HTTP callback server
