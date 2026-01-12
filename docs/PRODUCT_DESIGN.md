# TickTick MCP Enhanced - Product Design Document

## 1. Vision & Goal
To provide a frictionless, "modernized" TickTick integration for MCP clients that requires zero manual setup steps (like `pip install` or manual auth scripts). The user should only need to provide their credentials in the configuration file, and the tool should handle the rest.

## 2. Core Philosophy
**"Configuration is Installation"**
- No manual `git clone` dependencies if possible (future goal).
- No manual `python -m venv` or `pip install` commands.
- No manual `python -m ticktick_mcp.cli auth` steps separate from the main flow.
- **"Server First, Auth Second"**: The server should always start successfully given valid configuration, even if not yet authenticated.

## 3. Required Inputs
The system shall operate with **only** the following parameters provided by the user in their MCP Client configuration (e.g., `settings.json`):

1.  **Account Type** (`china` for dida365.com or `global` for ticktick.com)
2.  **Client ID** (from Developer Portal)
3.  **Client Secret** (from Developer Portal)

## 4. Modernized Architecture (The "uv" Way)
We will abandon the traditional `setup.py` legacy package structure in favor of a modern, standards-based approach using `pyproject.toml`.

### 4.1 Project Structure
- **`pyproject.toml`**: The single source of truth for dependencies and build configuration.
- **Dependency Management**: Handled dynamically by `uv`. The user never needs to touch `pip`.
- **Runtime**: The tool is executed via `uv run`, ensuring a clean, isolated environment every time.

### 4.2 Configuration Example (Gemini/Claude CLI)
The user's configuration file should look like this:

```json
"ticktick": {
  "command": "/path/to/uv",
  "args": [
    "run",
    "--directory", "/path/to/ticktick-mcp-enhanced",
    "ticktick-mcp",
    "run"
  ],
  "env": {
    "TICKTICK_ACCOUNT_TYPE": "china",
    "TICKTICK_CLIENT_ID": "your_client_id_here",
    "TICKTICK_CLIENT_SECRET": "your_client_secret_here"
  }
}
```

## 5. Toolset Redesign & Authentication Flow

The server will expose two categories of tools. The authentication process is now handled via tools, enabling the Agent to assist the user.

### 5.1 Administrative Tools (New)
These tools allow the Agent to manage the connection state without user CLI intervention.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| **`ticktick_status`** | None | Checks current connection status. Returns current user info if logged in, or a clear "Not Authenticated" status if not. |
| **`start_authentication`** | None | Initiates the OAuth flow. Returns the authorization URL that the user needs to visit. |
| **`finish_authentication`** | `code` (string) | Completes the OAuth flow. Exchanges the authorization code (pasted by the user) for an Access Token and persists it locally. |

### 5.2 Business Tools (Existing)
All existing task management tools remain available but will implement **Authentication Guard** logic.
- `get_project_info`, `create_tasks`, `query_tasks`, etc.

### 5.3 Behavior & Interaction Flow

**Scenario: User is NOT logged in (First run)**
1.  **User**: "What are my tasks for today?"
2.  **Agent**: Calls `query_tasks`.
3.  **MCP Server**: Detects missing/expired token. Returns:
    > `Error: Authentication required. Please use the 'start_authentication' tool to log in.`
4.  **Agent**: "I see you haven't logged in yet. Let me help you." -> Calls `start_authentication`.
5.  **MCP Server**: Returns:
    > `Please open this URL to authorize: https://ticktick.com/oauth/... Then copy the 'code' from the redirected URL.`
6.  **Agent**: Displays URL to user.
7.  **User**: Clicks link, authorizes, copies code. "Here is the code: abc123xyz".
8.  **Agent**: Calls `finish_authentication(code="abc123xyz")`.
9.  **MCP Server**: Verifies code, saves Token to `~/.ticktick_mcp_token.json`, returns Success.
10. **Agent**: "Login successful! Retrieving your tasks now..." -> Calls `query_tasks` again.
11. **MCP Server**: Returns task list.

### 5.4 Future Improvements: Local Callback Server & Configurable Redirect
To improve the user experience and avoid manual code copying, we plan to implement:
1.  **Local Callback Server**: The `start_authentication` tool can optionally spin up a temporary local HTTP server (e.g., on port 8000). When the user completes login, TickTick redirects to this local server, which automatically captures the code and completes the exchange.
2.  **Configurable Redirect URI**: The `redirect_uri` should not be hardcoded. It will be configurable via the `TICKTICK_REDIRECT_URI` environment variable, defaulting to `http://localhost:8000/callback` if not set. This allows users to deploy the MCP in environments where localhost is not suitable.

## 6. Implementation Plan
1.  **Refactor Build System**: Replace `setup.py` with `pyproject.toml`.
2.  **Config & Env**: Update `config.py` to read `CLIENT_ID`/`SECRET` from environment variables.
3.  **Auth Logic Internalization**: 
    - Move logic from `authenticate.py` into `src/auth.py`.
    - Implement file-based Token persistence (e.g., `token.json`).
    - Implement Token refresh logic.
4.  **Tool Implementation**: Register the 3 new auth tools in `server.py`.
5.  **Middleware**: Add an auth-check decorator to all business tools to trigger the "Error: Authentication required" response.