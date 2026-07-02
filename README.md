<p align="center">
  <img src="logo.png" width="128" alt="TickTick MCP Logo">
</p>

# 滴答清单 MCP 服务器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

[English Version is Here!](README_en.md)

这是一个基于滴答清单官方API的本地MCP服务，能让用户通过LLM和Agent应用轻松管理待办事项

🔗 **API 文档**: [滴答清单官方 OpenAPI](https://developer.dida365.com/docs#/openapi)

---

## 📢 Update

- **2026-07-02** 重构认证系统 — 移除环境变量配置，改为运行时 `login` 工具直接传入 OAuth 凭据，支持中国版/国际版一键切换。
- **2026-05-12** 提取工具描述 — 将所有工具的 Prompt 提取为独立 `.txt` 文件，便于维护和修改。
- **2026-05-09** 新增提醒参数 — 创建和更新任务时支持 `reminders`，可设置到期前推送提醒。
- **2026-01-29** 项目结构重构 — 迁移到 `src` 目录布局，代码组织更规范。
- **2026-01-17** 日志系统升级 — 改为基于会话的纯文件日志，交互追踪更清晰。
- **2026-01-12** 全面重构 — 实现无缝本地 OAuth 回调认证、统一日志追踪、移除 python-dotenv 依赖。
- **2025-12-07** 修复时区处理问题。
- **2025-10-17** 优化优先级参数自然语言映射及认证流程。

## ✨ 功能特性

- **🤖 让 AI Agent 管理你的任务**：通过自然语言指令创建、查询、更新和完成任务
- **🔑 运行时 OAuth 认证**：通过 `login` 工具直接传入凭据，浏览器自动打开授权页面，无需配置环境变量
- **📅 任务管理**：支持创建任务、项目、子任务，以及复杂的查询功能
- **🔍 高级查询**：按日期范围、优先级、关键词等多维度筛选任务

## 🚀 安装与使用

### 前置条件

- **Python 版本**：3.10 或更高
- **LLM 客户端**（如 Claude Desktop、OpenCode 等）

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced.git
cd ticktick-mcp-enhanced

# 创建虚拟环境并安装
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

uv pip install -e .
```

### 配置 LLM 客户端

在 Claude Desktop 或其他 LLM 应用的配置文件中添加：

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ticktick": {
      "command": ["/path/to/ticktick-mcp-enhanced/.venv/bin/ticktick-mcp"],
      "enabled": true
    }
  }
}
```

> **注意**：将 `/path/to/ticktick-mcp-enhanced` 替换为项目的实际绝对路径。Windows 用户请使用双反斜杠 `\\` 或正斜杠 `/`。

### 🔑 获取 API 凭证

在 [滴答清单开发者中心](https://developer.dida365.com/manage)（国内账号）或 [TickTick Developer Center](https://developer.ticktick.com/manage)（国外账号）注册一个应用。

1. 点击 **"New App"**
2. 设置 **Redirect URI** 为 `http://localhost:8000/callback`
3. 保存你的 **Client ID** 和 **Client Secret**

### 使用方法

1. **重启 LLM 客户端**
2. **登录滴答清单**
   - 在对话中输入："帮我登录滴答清单"，并提供你的 Client ID 和 Client Secret
   - AI 会调用 `login` 工具，浏览器自动打开滴答清单授权页
   - 在浏览器中点击允许，完成授权
   - 登录状态保存在本地，后续使用无需重复登录
3. **开始使用**
   - 查看任务："查看我今天的任务"
   - 创建任务："创建一个任务：明天下午3点开会"
   - 查询项目："查看所有清单"

## 🧰 可用工具

此 MCP 向你的 LLM 客户端公开以下工具。

| 类别     | 工具名称           | 功能描述                                       |
| :------- | :----------------- | :--------------------------------------------- |
| **认证** | `ticktick_status`  | 检查当前的连接和授权状态。                     |
|          | `login`            | 传入 OAuth 凭据，启动浏览器授权流程并完成登录。 |
| **清单** | `get_all_projects` | 获取所有清单列表。                             |
|          | `get_project_info` | 查看特定清单及其中的任务。                     |
|          | `create_project`   | 创建一个新的项目。                             |
|          | `delete_projects`  | 删除项目。                                     |
| **任务** | `create_tasks`     | 创建任务（支持智能时间识别）。                 |
|          | `update_tasks`     | 修改任务标题、内容、日期或优先级。             |
|          | `complete_tasks`   | 将任务标记为完成。                             |
|          | `delete_tasks`     | 批量删除任务。                                 |
|          | `create_subtasks`  | 为任务添加子任务。                             |
| **查询** | `query_tasks`      | 高级清单查询（支持日期范围、优先级、搜索词）。 |

## 📂 项目结构

```text
ticktick-mcp-enhanced/
├── src/
│   └── ticktick_mcp/
│       ├── __init__.py          # 包入口
│       ├── server.py            # MCP 服务入口
│       ├── auth.py              # OAuth 逻辑与回调服务器
│       ├── client_manager.py    # 客户端管理
│       ├── log.py               # 日志配置
│       ├── ticktick_client.py   # TickTick API 客户端
│       ├── tools/               # 各类工具实现
│       │   └── prompts/         # 工具描述 (.txt)
│       └── utils/               # 格式化与校验工具
├── pyproject.toml              # 项目配置与依赖
└── README.md                  # 本文档
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [滴答清单 Open API](https://developer.dida365.com/docs#/openapi)
- [FastMCP](https://github.com/jlowin/fastmcp)
