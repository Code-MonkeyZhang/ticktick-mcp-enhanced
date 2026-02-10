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

# Run the CLI
uv run ticktick --help                # Show help with usage examples
uv run ticktick -h                    # Short help option (same as --help)
uv run ticktick                       # No args also shows help with examples

# Top-level commands (flattened)
uv run ticktick list                  # List all tasks
uv run ticktick today                 # Show tasks due today
uv run ticktick overdue               # Show overdue tasks
uv run ticktick projects              # List all projects

# Authentication (interactive configuration)
uv run ticktick auth login            # First-time setup prompts for credentials
uv run ticktick auth status
uv run ticktick auth logout

# Subcommands for advanced operations
uv run ticktick tasks list
uv run ticktick tasks create
uv run ticktick tasks complete
uv run ticktick projects create

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
| **Auth Manager** | `auth.py` | OAuth 2.0 flow, token storage/loading, local callback server |
| **Config Manager** | `config.py` | Persistent OAuth configuration storage (~/.ticktick/config.json) |
| **API Client** | `ticktick_client.py` | HTTP requests to TickTick API |
| **Client Manager** | `client_manager.py` | Global singleton client instance (`ticktick` variable) |
| **Logging** | `log.py` | Session-based file logging (strictly file-only, no stdout) |
| **CLI** | `cli/` | Typer-based command-line interface |

### CLI Structure

The CLI is organized under `src/ticktick_mcp/cli/`:

```
cli/
├── __init__.py         # Version info
├── main.py             # Main entry point (ticktick command)
├── console.py          # Rich console utilities and table rendering
├── context.py          # CLI context management (auth, client)
└── commands/
    ├── auth.py         # Authentication commands
    ├── tasks.py        # Task management commands
    └── projects.py     # Project management commands
```

**Top-Level Commands (Flattened):**
- `ticktick list [-p PROJECT] [--priority PRIORITY] [-s SEARCH]` - List tasks with filters
- `ticktick today` - Show tasks due today
- `ticktick overdue` - Show overdue tasks
- `ticktick projects` - List all projects
- `ticktick -h` / `ticktick` - Show help with usage examples

**Authentication Commands:**
- `ticktick auth login` - Interactive OAuth setup (prompts for credentials)
- `ticktick auth status` - Check authentication status
- `ticktick auth logout` - Clear token and configuration
- `ticktick auth finish <code>` - Complete OAuth with manual code

**Task Commands:**
- `ticktick tasks list/today/overdue/create/complete/delete/view`

**Project Commands:**
- `ticktick projects list/create/view/delete`

### Configuration Persistence

OAuth credentials are now persisted to `~/.ticktick/config.json`:

```json
{
  "account_type": "china",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "redirect_uri": "http://localhost:8000/callback"
}
```

**Configuration Priority:**
1. Config file (`~/.ticktick/config.json`)
2. Environment variables (`TICKTICK_*`)
3. Default values

**First-time Setup:**
Run `ticktick auth login` to interactively configure:
- Account type (China/Global)
- Client ID
- Client Secret
- Redirect URI (must match OAuth app registration)

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
5. **Configuration Persistence**: OAuth credentials saved to `~/.ticktick/config.json`
6. **Unified Help**: All commands support `-h` as short option for `--help`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TICKTICK_ACCOUNT_TYPE` | `"china"` or `"global"` | `"global"` |
| `TICKTICK_CLIENT_ID` | OAuth client ID | - |
| `TICKTICK_CLIENT_SECRET` | OAuth client secret | - |
| `TICKTICK_REDIRECT_URI` | Callback URL | `http://localhost:8000/callback` |
| `TICKTICK_DISPLAY_TIMEZONE` | Display timezone | `"Local"` |
| `MCP_LOG_ENABLE` | Enable file logging (`"true"` or `"false"`) | `"false"` |

**Note**: Environment variables are optional if credentials are configured via `ticktick auth login`.

## Testing

### Unit Tests

```bash
# Run all unit tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src/ticktick_mcp --cov-report=term

# Run specific test file
uv run pytest tests/test_cli_console.py
uv run pytest tests/test_config.py
```

### Integration Tests

Integration tests require real API credentials and make actual API calls:

```bash
# Set environment variables and run integration tests
export TICKTICK_CLIENT_ID="your_client_id"
export TICKTICK_CLIENT_SECRET="your_client_secret"
export TICKTICK_RUN_INTEGRATION_TESTS=1

# First authenticate
uv run ticktick auth login

# Then run integration tests
uv run pytest tests/integration/ -v
```

**Warning**: Integration tests will create, modify, and delete real tasks/projects in your TickTick account. Use a test account!
