# TickTick MCP Server

[English](#english) | [中文](#中文)

---

## English

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that allows you manage your daily routine TickTick task with LLMs!

### Features

- 📋 View & Search all your TickTick projects and tasks
- ✏️ Create new projects, tasks, and subtasks through natural language
- 🔄 Update existing task details (title, content, dates, priority)
- 🗑️ Delete tasks and projects (single or batch)
- 🔌 Seamless integration with Claude Desktop and other LLM applications

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- TickTick account with API access
- TickTick API credentials (Client ID, Client Secret)

### Authentication

You need to have a TickTick account to use this MCP.

Register your application at the [TickTick Developer Center](https://developer.ticktick.com/manage). If you are using Chinese version, at [Dida Developer Center](https://developer.dida365.com/manage).

- Click "New App"
- Set the redirect URI. The default used by this MCP is `http://localhost:8000/callback`.
  - You can customize this by setting the `TICKTICK_REDIRECT_URI` environment variable if needed.
- Keep your Client ID and Client Secret

### Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced
   cd ticktick-mcp
   ```

2. **Install with uv**:

   ```bash
   # Install uv if you don't have it already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create a virtual environment
   uv venv

   # Activate the virtual environment
   source .venv/bin/activate

   # Install the package
   uv pip install -e .
   ```

3. **Authenticate with TickTick**:

   ```bash
   # Run authentication
   uv run -m ticktick_mcp.cli auth
   ```

   This will:

   - Ask for your TickTick Client ID and Client Secret
   - Open a browser window for you to log in to TickTick
   - Automatically save your access tokens to a `.env` file

4. **Test your configuration**:

   ```bash
   uv run test_server.py
   ```

### Use MCP in Claude Desktop and other LLM applicaitons

1. Install [Claude for Desktop](https://claude.ai/download)
2. Edit your Claude configuration file:

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add the TickTick MCP server configuration:

   ```json
   {
     "mcpServers": {
       "ticktick": {
         "command": "<absolute path to uv>",
         "args": [
           "run",
           "--directory",
           "<absolute path to ticktick-mcp directory>",
           "-m",
           "ticktick_mcp.cli",
           "run"
         ],
         "env": {
           "TICKTICK_CLIENT_ID": "your_client_id",
           "TICKTICK_CLIENT_SECRET": "your_client_secret",
           "TICKTICK_REDIRECT_URI": "http://localhost:8000/callback"
         }
       }
     }
   }
   ```

4. Restart Claude for Desktop

### Available Tools

All 10 MCP tools in one place:

| Category     | Tool               | Description                                  | Key Parameters                                                                                                                                                                     |
| ------------ | ------------------ | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Projects** | `get_all_projects` | List all TickTick projects                   | None                                                                                                                                                                               |
|              | `get_project_info` | Get project details with all tasks           | `project_id` (use `"inbox"` for inbox)                                                                                                                                             |
|              | `create_project`   | Create a new project                         | `name`, `color`, `view_mode`                                                                                                                                                       |
|              | `delete_projects`  | Delete one or more projects                  | `projects` (ID or list of IDs)                                                                                                                                                     |
| **Tasks**    | `create_tasks`     | Create one or more tasks                     | `tasks` (dict or list of dicts)``Required: `title`, `project_id`Optional: `priority`, `due_date`, `content`, etc.                                                                  |
|              | `update_tasks`     | Update one or more tasks                     | `tasks` (dict or list of dicts)``Required: `task_id`, `project_id`Optional: `title`, `priority`, `due_date`, etc.                                                                  |
|              | `complete_tasks`   | Mark tasks as complete                       | `tasks` (dict or list of dicts)``Required: `project_id`, `task_id`                                                                                                                 |
|              | `delete_tasks`     | Delete one or more tasks                     | `tasks` (dict or list of dicts)``Required: `project_id`, `task_id`                                                                                                                 |
|              | `create_subtasks`  | Create one or more subtasks                  | `subtasks` (dict or list of dicts)``Required: `subtask_title`, `parent_task_id`, `project_id`                                                                                      |
| **Query**    | `query_tasks`      | Unified query with multi-dimensional filters | `task_id`, `project_id`, `priority` (`"high"`, `"medium"`, `"low"`, `"none"`), `date_filter` (`"today"`, `"tomorrow"`, `"overdue"`, `"next_7_days"`), `custom_days`, `search_term` |

### Example Usage

**Query Examples:**

```python
# All tasks
query_tasks()

# Inbox tasks
query_tasks(project_id="inbox")

# High priority tasks due today
query_tasks(priority="high", date_filter="today")

# Search for meetings
query_tasks(search_term="meeting")

# Specific task lookup
query_tasks(task_id="abc123", project_id="xyz789")
```

**Batch Operations:**

```python
# Create multiple tasks
create_tasks([
    {"title": "Task 1", "project_id": "inbox", "priority": "high"},
    {"title": "Task 2", "project_id": "work", "priority": "medium"}
])

# Update multiple tasks
update_tasks([
    {"task_id": "abc", "project_id": "123", "priority": "high"},
    {"task_id": "def", "project_id": "123", "title": "Updated"}
])

# Complete multiple tasks
complete_tasks([
    {"project_id": "inbox", "task_id": "abc"},
    {"project_id": "work", "task_id": "def"}
])
```

### Example Prompts

**General:**

- "Show me all my TickTick projects"
- "What's in my inbox?"
- "Create a task 'Buy groceries' with high priority"
- "Show me all high priority tasks due today"
- "Create these three tasks: 'Buy groceries', 'Call mom', and 'Finish report'"
- "Mark all overdue tasks as complete"
- "Delete all completed tasks from archive"
- "Show me high priority tasks in my Work project"
- "Find all tasks with 'meeting' due this week"
- "What tasks are overdue in my inbox?"

### Project Structure

```
ticktick-mcp/
├── ticktick_mcp/
│   ├── src/
│   │   ├── server.py          # MCP server core (45 lines)
│   │   ├── config.py          # Configuration management
│   │   ├── ticktick_client.py # TickTick API client
│   │   ├── auth.py            # OAuth implementation
│   │   ├── tools/             # MCP tools (modular)
│   │   │   ├── project_tools.py
│   │   │   ├── task_tools.py
│   │   │   └── query_tools.py
│   │   └── utils/             # Utilities
│   │       ├── timezone.py
│   │       ├── formatters.py
│   │       └── validators.py
│   ├── cli.py                 # CLI interface
│   └── authenticate.py        # Auth utility
├── test/                      # Comprehensive tests
├── doc/
│   └── CUROR_MEMORY.md        # Development history
├── README.md
├── requirements.txt
└── setup.py
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is licensed under the MIT License.

### Attribution

This project is inspired by and contains code derived from:

- [ticktick-mcp](https://github.com/jacepark12/ticktick-mcp) by Jaesung Park, licensed under MIT License

---

## 中文

一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的服务器，让你可以用大模型管理 TickTick 的日常任务。

### 功能特性

- 📋 查看并搜索所有 TickTick 项目与任务
- ✏️ 通过自然语言创建项目、任务与子任务
- 🔄 更新任务详情（标题、内容、日期、优先级）
- 🗑️ 删除任务和项目（单个或批量）
- 🔌 无缝集成 Claude Desktop 及其他 LLM 应用

### 环境要求

- Python 3.10 及以上
- [uv](https://github.com/astral-sh/uv) —— 快速的 Python 包安装与解析工具
- 具备 API 权限的 TickTick 账号
- TickTick API 凭证（Client ID 与 Client Secret）

### 身份验证

使用本 MCP 前，需要拥有 TickTick 账号。

在 [TickTick 开发者中心](https://developer.ticktick.com/manage) 注册应用。若使用国内版，请前往 [滴答清单开发者中心](https://developer.dida365.com/manage)。

- 点击 “New App”
- 将重定向地址设为 `http://localhost:8000/callback`
- 保存好 Client ID 和 Client Secret

### 安装步骤

1. **克隆仓库**：

   ```bash
   git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced
   cd ticktick-mcp
   ```

2. **使用 uv 安装**：

   ```bash
   # 如果尚未安装 uv，先执行：
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 创建虚拟环境
   uv venv

   # 激活虚拟环境
   source .venv/bin/activate

   # 安装依赖
   uv pip install -e .
   ```

3. **完成 TickTick 登录授权**：

   ```bash
   # 运行授权流程
   uv run -m ticktick_mcp.cli auth
   ```

   这一步会：

   - 询问你的 TickTick Client ID 和 Client Secret
   - 打开浏览器窗口完成 TickTick 登录
   - 自动将访问令牌保存到 `.env` 文件

4. **测试配置**：

   ```bash
   uv run test_server.py
   ```

### 在 Claude Desktop 和其他 LLM 中使用 MCP

1. 安装 [Claude for Desktop](https://claude.ai/download)
2. 编辑 Claude 配置文件：

   - **macOS**：`~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**：`%APPDATA%\\Claude\\claude_desktop_config.json`

3. 添加 TickTick MCP 服务器配置：

   ```json
   {
     "mcpServers": {
       "ticktick": {
         "command": "<absolute path to uv>",
         "args": [
           "run",
           "--directory",
           "<absolute path to ticktick-mcp directory>",
           "-m",
           "ticktick_mcp.cli",
           "run"
         ]
       }
     }
   }
   ```

4. 重启 Claude Desktop

### 可用工具

10 个 MCP 工具一览：

| 分类         | 工具名              | 功能描述                          | 关键参数                                                                                                                                                                           |
| ------------ | ------------------ | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Projects** | `get_all_projects` | 列出全部 TickTick 项目            | None                                                                                                                                                                               |
|              | `get_project_info` | 获取项目详情及其中的所有任务      | `project_id`（收件箱使用 `"inbox"`）                                                                                                                                                |
|              | `create_project`   | 创建新项目                        | `name`, `color`, `view_mode`                                                                                                                                                       |
|              | `delete_projects`  | 删除一个或多个项目                | `projects`（单个 ID 或 ID 列表）                                                                                                                                                   |
| **Tasks**    | `create_tasks`     | 创建一个或多个任务                | `tasks`（字典或字典列表）``必填：`title`, `project_id`可选：`priority`, `due_date`, `content` 等                                                                                   |
|              | `update_tasks`     | 更新一个或多个任务                | `tasks`（字典或字典列表）``必填：`task_id`, `project_id`可选：`title`, `priority`, `due_date` 等                                                                                   |
|              | `complete_tasks`   | 将任务标记为完成                  | `tasks`（字典或字典列表）``必填：`project_id`, `task_id`                                                                                                                           |
|              | `delete_tasks`     | 删除一个或多个任务                | `tasks`（字典或字典列表）``必填：`project_id`, `task_id`                                                                                                                           |
|              | `create_subtasks`  | 创建一个或多个子任务              | `subtasks`（字典或字典列表）``必填：`subtask_title`, `parent_task_id`, `project_id`                                                                                                |
| **Query**    | `query_tasks`      | 多维度过滤的统一查询              | `task_id`, `project_id`, `priority`（`"high"`, `"medium"`, `"low"`, `"none"`），`date_filter`（`"today"`, `"tomorrow"`, `"overdue"`, `"next_7_days"`），`custom_days`, `search_term` |

### 使用示例

**查询示例：**

```python
# 查询所有任务
query_tasks()

# 查询收件箱任务
query_tasks(project_id="inbox")

# 查询今天到期的高优先级任务
query_tasks(priority="high", date_filter="today")

# 搜索包含会议的任务
query_tasks(search_term="meeting")

# 查询指定任务
query_tasks(task_id="abc123", project_id="xyz789")
```

**批量操作：**

```python
# 批量创建任务
create_tasks([
    {"title": "Task 1", "project_id": "inbox", "priority": "high"},
    {"title": "Task 2", "project_id": "work", "priority": "medium"}
])

# 批量更新任务
update_tasks([
    {"task_id": "abc", "project_id": "123", "priority": "high"},
    {"task_id": "def", "project_id": "123", "title": "Updated"}
])

# 批量完成任务
complete_tasks([
    {"project_id": "inbox", "task_id": "abc"},
    {"project_id": "work", "task_id": "def"}
])
```

### 提示词示例

**常用：**

- “展示我所有的 TickTick 项目”
- “收件箱里有什么？”
- “创建一个名为 ‘Buy groceries’、高优先级的任务”
- “显示今天到期的所有高优先级任务”
- “帮我创建这三个任务：‘Buy groceries’、‘Call mom’、‘Finish report’”
- “把所有逾期任务标记为完成”
- “从归档中删除所有已完成任务”
- “展示 Work 项目下的高优先级任务”
- “找出本周包含 ‘meeting’ 的任务”
- “收件箱里哪些任务已逾期？”

### 项目结构

```
ticktick-mcp/
├── ticktick_mcp/
│   ├── src/
│   │   ├── server.py          # MCP 服务器核心（45 行）
│   │   ├── config.py          # 配置管理
│   │   ├── ticktick_client.py # TickTick API 客户端
│   │   ├── auth.py            # OAuth 实现
│   │   ├── tools/             # MCP 工具（模块化）
│   │   │   ├── project_tools.py
│   │   │   ├── task_tools.py
│   │   │   └── query_tools.py
│   │   └── utils/             # 工具方法
│   │       ├── timezone.py
│   │       ├── formatters.py
│   │       └── validators.py
│   ├── cli.py                 # CLI 接口
│   └── authenticate.py        # 授权工具
├── test/                      # 测试用例
├── doc/
│   └── CUROR_MEMORY.md        # 开发记录
├── README.md
├── requirements.txt
└── setup.py
```

### 贡献

欢迎贡献代码，欢迎提交 Pull Request。

### 许可证

本项目采用 MIT License。

### 致谢

本项目受以下项目启发并包含其派生代码：

- [ticktick-mcp](https://github.com/jacepark12/ticktick-mcp)，作者 Jaesung Park，基于 MIT License

---

## OpenCode MCP 配置

在 OpenCode 中使用此 MCP 服务器时，可能会遇到以下问题：

### 问题：ModuleNotFoundError: No module named 'ticktick_mcp'

**原因**：
虚拟环境中未安装该包，Python 无法找到 `ticktick_mcp` 模块。

**解决方案**：
使用 `uv pip install -e .` 将包安装到虚拟环境：

```bash
cd ticktick-mcp-enhanced
uv pip install -e .
```

这会在虚拟环境的 `site-packages` 中创建一个 `.egg-link` 文件，指向项目目录，使 Python 能够找到模块。

### OpenCode 配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "ticktick": {
      "type": "local",
      "command": [
        "/path/to/.venv/bin/python",
        "-m",
        "ticktick_mcp.cli",
        "run"
      ],
      "environment": {
        "SSL_CERT_FILE": "/path/to/.venv/lib/python3.11/site-packages/certifi/cacert.pem",
        "REQUESTS_CA_BUNDLE": "/path/to/.venv/lib/python3.11/site-packages/certifi/cacert.pem"
      },
      "enabled": true
    }
  }
}
```

**注意**：在使用 `uv pip install -e .` 之前，必须先确保包已正确安装到虚拟环境中。
