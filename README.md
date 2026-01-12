# TickTick MCP Enhanced

[English](#english) | [中文](#中文)

---

## English

A modernized [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that allows you to manage your TickTick tasks with LLMs using a "Configuration is Installation" philosophy.

### Features

- 🚀 **Configuration is Installation**: No manual setup scripts. Just configure your MCP client and go.
- 🔐 **Interactive Authentication**: Secure, in-chat OAuth flow with automatic local callback handling.
- 📋 **Comprehensive Management**: View, create, update, and delete projects and tasks.
- 🔍 **Smart Query**: Unified search with natural language filtering (dates, priorities, keywords).
- 🔌 **Universal Compatibility**: Works seamlessly with Claude Desktop, Gemini CLI, and other MCP clients.

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (Recommended) or Python pip
- TickTick account with API access
- TickTick API credentials (Client ID, Client Secret)

### Authentication Setup

You need to register an application at the [TickTick Developer Center](https://developer.ticktick.com/manage) (or [Dida Developer Center](https://developer.dida365.com/manage) for CN users).

1. Click "New App".
2. Set **Redirect URI**.
   - **Recommended**: `http://localhost:8000/callback` (Default used by this MCP).
   - *Custom*: If you need a different port, set `TICKTICK_REDIRECT_URI` in your config to match.
3. Keep your **Client ID** and **Client Secret**.

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced
   cd ticktick-mcp-enhanced
   ```

2. **Configure your MCP Client** (e.g., Claude Desktop `claude_desktop_config.json`):

   ```json
   {
     "mcpServers": {
       "ticktick": {
         "command": "/path/to/uv",  // Absolute path to 'uv'
         "args": [
           "run",
           "--directory",
           "/absolute/path/to/ticktick-mcp-enhanced", // Absolute path to cloned repo
           "ticktick-mcp",
           "run"
         ],
         "env": {
           "TICKTICK_ACCOUNT_TYPE": "china", // 'china' (dida365) or 'global' (ticktick.com)
           "TICKTICK_CLIENT_ID": "your_client_id_here",
           "TICKTICK_CLIENT_SECRET": "your_client_secret_here",
           "TICKTICK_REDIRECT_URI": "http://localhost:8000/callback" // Optional
         }
       }
     }
   }
   ```

3. **Use it!**
   - Open your AI Agent.
   - Ask: "What are my tasks for today?"
   - If not logged in, the Agent will provide an authorization link.
   - **Click the link** -> Log in -> **Done!** (The page will auto-close).

   *Token is stored in `.ticktick_token.json` in the project directory.*

### Available Tools

| Category | Tool | Description |
| :--- | :--- | :--- |
| **Auth** | `ticktick_status` | Check connection status. |
| | `start_authentication` | Generate login link (starts local listener). |
| | `finish_authentication` | Manual code exchange (fallback). |
| **Projects** | `get_all_projects` | List all projects. |
| | `get_project_info` | Get tasks in a project. |
| | `create_project` | Create a new project. |
| | `delete_projects` | Delete projects. |
| **Tasks** | `create_tasks` | Create tasks (smart parsing). |
| | `update_tasks` | Update task details. |
| | `complete_tasks` | Mark tasks as complete. |
| | `delete_tasks` | Delete tasks. |
| | `create_subtasks` | Add subtasks. |
| **Query** | `query_tasks` | Powerful filter (date, priority, search). |

---

## 中文

一个现代化的 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器，让大模型通过“配置即安装”的方式管理你的滴答清单。

### 功能特性

- 🚀 **配置即安装**：无需运行安装脚本。配置好 MCP 客户端即可直接使用。
- 🔐 **交互式认证**：在聊天中直接完成 OAuth 认证，支持本地自动回调，无需复制粘贴。
- 📋 **全面管理**：支持查看、创建、更新、删除项目和任务。
- 🔍 **智能查询**：支持按日期、优先级、关键词进行自然语言过滤。
- 🔌 **广泛兼容**：完美支持 Claude Desktop, Gemini CLI 等 MCP 客户端。

### 准备工作

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (推荐)
- 滴答清单账号
- API 凭证 (Client ID, Client Secret)

### 认证设置

前往 [滴答清单开发者中心](https://developer.dida365.com/manage) (国内) 或 [TickTick Developer Center](https://developer.ticktick.com/manage) (国际) 注册应用。

1. 点击 "New App"。
2. 设置 **Redirect URI**。
   - **推荐**: `http://localhost:8000/callback` (本工具默认值)。
   - *自定义*: 如需修改端口，请在配置中设置 `TICKTICK_REDIRECT_URI` 环境变量。
3. 保存 **Client ID** 和 **Client Secret**。

### 快速开始

1. **克隆代码库**:
   ```bash
   git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced
   cd ticktick-mcp-enhanced
   ```

2. **配置 MCP 客户端** (如 Claude Desktop `claude_desktop_config.json`):

   ```json
   {
     "mcpServers": {
       "ticktick": {
         "command": "/path/to/uv",  // uv 的绝对路径
         "args": [
           "run",
           "--directory",
           "/absolute/path/to/ticktick-mcp-enhanced", // 项目文件夹绝对路径
           "ticktick-mcp",
           "run"
         ],
         "env": {
           "TICKTICK_ACCOUNT_TYPE": "china", // china (国内版) 或 global (国际版)
           "TICKTICK_CLIENT_ID": "你的Client ID",
           "TICKTICK_CLIENT_SECRET": "你的Client Secret",
           "TICKTICK_REDIRECT_URI": "http://localhost:8000/callback" // 可选
         }
       }
     }
   }
   ```

3. **开始使用**:
   - 打开你的 AI 助手。
   - 问它：“我今天有什么任务？”
   - 如果未登录，助手会给你一个链接。
   - **点击链接** -> 登录授权 -> **完成！** (页面会自动关闭)。
   - 助手会自动获取 Token 并继续回答你的问题。

   *Token 会安全存储在项目目录下的 `.ticktick_token.json` 文件中。*

### 项目结构

```
ticktick-mcp-enhanced/
├── ticktick_mcp/
│   ├── src/
│   │   ├── server.py          # MCP Server 入口
│   │   ├── auth.py            # OAuth 认证与本地回调服务器
│   │   ├── tools/             # 工具实现
│   │   └── ...
│   └── cli.py                 # CLI 包装器
├── pyproject.toml             # 项目依赖配置
├── README.md
└── .ticktick_token.json       # 本地凭证 (被 git 忽略)
```

### 许可证

MIT License