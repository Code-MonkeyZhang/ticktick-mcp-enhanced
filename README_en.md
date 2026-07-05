<p align="center">
  <img src="logo.png" width="128" alt="TickTick MCP Logo">
</p>

# TickTick MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that allows LLMs to manage your TickTick/Dida365 to-do lists.

🔗 **API Documentation**: [TickTick/Dida365 OpenAPI](https://developer.dida365.com/docs#/openapi)

---

## 🛠️ Prerequisites

- **Python 3.10+**
- [**uv**](https://github.com/astral-sh/uv) installed (Recommended)
- A TickTick or Dida365 account
- API Credentials (Client ID, Client Secret)

## 🔑 Auth Setup

Register an application at the [TickTick Developer Center](https://developer.ticktick.com/manage) (or [Dida Developer Center](https://developer.dida365.com/manage) for CN users).

1. Click **"New App"**.
2. Save your **Client ID** and **Client Secret**.
3. Set **Redirect URI**:
   - **Recommended**: `http://localhost:8000/callback` .
   - _Custom_: If you change this, set the `TICKTICK_REDIRECT_URI` environment variable accordingly.

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced
cd ticktick-mcp-enhanced
```

### 2. Configure your MCP Client

Example for **Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/ticktick-mcp-enhanced",
        "ticktick-mcp",
        "run"
      ],
      "env": {
        "TICKTICK_ACCOUNT_TYPE": "china", // "china" or "global"
        "TICKTICK_CLIENT_ID": "your_client_id_here",
        "TICKTICK_CLIENT_SECRET": "your_client_secret_here",
        "TICKTICK_REDIRECT_URI": "http://localhost:8000/callback",
        "MCP_LOG_ENABLE": "true" // Optional: Enable file logging (logs/session_*.log), no stderr output
      }
    }
  }
}
```

### 3. Authorize and Use

1. Restart your MCP client.
2. Ask the AI: "Show my tasks for today."
3. **First-time Auth**: The AI will provide an authorization link. Click it -> Log in -> A auth page will pop up shows auth is compeleted.
4. You can go back to LLM client and use this mcp to access TickTick

> Your auth tokens will be stored in `.ticktick_token.json` within the project folder.

## 🧰 Available Tools

This MCP exposes the following tools to your LLM client.

| Category     | Tool                   | Description                                        |
| :----------- | :--------------------- | :------------------------------------------------- |
| **Auth**     | `ticktick_status`      | Check current connection and auth status.          |
|              | `login`                | Pass OAuth credentials and run the browser auth flow to log in. |
| **Projects** | `get_all_projects`     | List all projects.                                 |
|              | `get_project_info`     | View a specific project and the tasks in it.       |
|              | `create_project`       | Create a new project.                              |
|              | `update_projects`      | Update a project's name, color, view mode or kind in place (batch supported). |
|              | `delete_projects`      | Delete projects.                                   |
| **Tasks**    | `create_tasks`         | Create tasks with smart time parsing.              |
|              | `update_tasks`         | Update title, content, date, or priority.          |
|              | `complete_tasks`       | Mark tasks as completed.                           |
|              | `delete_tasks`         | Batch delete tasks.                                |
|              | `create_subtasks`      | Add subtasks to an existing task.                  |
|              | `move_tasks`           | Move tasks between projects (batch supported).     |
| **Query**    | `query_tasks`          | Advanced filtering (date range, priority, search). |
|              | `get_completed_tasks`  | Query completed tasks by project and time range.   |
| **Habits**   | `get_all_habits`       | List all habits.                                   |
|              | `get_habit`            | Get a single habit by ID.                          |
|              | `create_habits`        | Create habits (batch supported).                   |
|              | `update_habits`        | Update habit attributes in place (batch supported). |
|              | `checkin_habits`       | Check in a habit, defaulting to today (batch and backfill supported). |
|              | `get_habit_checkins`   | Query habit check-in records by date range.        |

## 📂 Project Structure

```text
ticktick-mcp-enhanced/
├── ticktick_mcp/
│   ├── src/
│   │   ├── server.py          # MCP Server entry point
│   │   ├── auth.py            # OAuth & callback server
│   │   ├── tools/             # Tool implementations
│   │   └── utils/             # Formatters & validators
│   └── __main__.py            # CLI entry point
├── pyproject.toml             # Project metadata & deps
└── README.md                  # Main documentation (Chinese)
```