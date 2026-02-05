<p align="center">
  <img src="logo.png" width="128" alt="TickTick MCP Logo">
</p>

# 滴答清单 MCP 服务器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

一个 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器，允许大语言模型管理你的滴答清单/TickTick 待办事项。

🔗 **API 文档**: [滴答清单官方 OpenAPI](https://developer.dida365.com/docs#/openapi)

---

## ✨ 功能特性

- **🤖 让 AI Agent 管理你的任务**：通过自然语言指令创建、查询、更新和完成任务
- **🔑 OAuth 2.0 安全认证**：基于官方 OAuth 2.0 登录流程，支持滴答清单国际版和国内版
- **📅 任务管理**：支持创建任务、项目、子任务，以及复杂的查询功能
- **🔍 高级查询**：按日期范围、优先级、关键词等多维度筛选任务

## 🚀 安装与使用

```bash
# 克隆项目
git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced.git
cd ticktick-mcp-enhanced

# 将项目安装到环境
uv pip install -e .
```

### 在 LLM 应用中配置 MCP

在 Claude Desktop 或其他 LLM 应用的配置文件中添加：

```json
{
  "mcpServers": {
    "ticktick": {
      "command": ["/path/to/ticktick-mcp-enhanced/.venv/bin/ticktick-mcp"],
      "env": {
        "TICKTICK_ACCOUNT_TYPE": "china",
        "TICKTICK_CLIENT_ID": "你的_client_id",
        "TICKTICK_CLIENT_SECRET": "你的_client_secret",
        "TICKTICK_REDIRECT_URI": "http://localhost:8000/callback"
      }
    }
  }
}
```

> **注意**：
>
> - 将 `/path/to/ticktick-mcp-enhanced` 替换为项目的实际路径
> - `TICKTICK_ACCOUNT_TYPE`：国内用户填 `"china"`，国际用户填 `"global"`
> - `TICKTICK_CLIENT_ID`：在滴答清单开发者中心获取的CLIENT_ID
> - `TICKTICK_CLIENT_SECRET`：在滴答清单开发者中心获取的CLIENT_SECRET
> - `TICKTICK_REDIRECT_URI`：在滴答清单开发者中心配置的URL

### 🔑 获取 API 凭证

在 [滴答清单开发者中心](https://developer.dida365.com/manage)（国内账号）或 [TickTick Developer Center](https://developer.ticktick.com/manage) (国外账号) 注册一个应用。

1. 点击 **"New App"**。
2. 保存你的 **Client ID** 和 **Client Secret**。
3. 设置 **Redirect URI**：
   - **默认使用**: `http://localhost:8000/callback`。
   - _自定义_: 如果你修改了此项，请相应地设置 `TICKTICK_REDIRECT_URI` 环境变量。

### 5. 打开 LLM App

重启你使用的 LLM 应用。

### 6. 点击网址进行登录

在对话中输入："帮我开始认证滴答清单"，AI 会返回授权链接，点击后登录并授权。

### 7. 愉快使用

- 查看任务："查看我今天的任务"
- 创建任务："创建一个任务：明天下午3点开会"
- 查询项目："查看所有清单"

## 🧰 可用工具

此 MCP 向你的 LLM 客户端公开以下工具。

| 类别     | 工具名称               | 功能描述                                       |
| :------- | :--------------------- | :--------------------------------------------- |
| **认证** | `ticktick_status`      | 检查当前的连接和授权状态。                     |
|          | `start_authentication` | 生成登录链接并启动本地回调监听。               |
| **清单** | `get_all_projects`     | 获取所有清单列表。                             |
|          | `get_project_info`     | 查看特定清单及其中的任务。                     |
|          | `create_project`       | 创建一个新的项目。                             |
|          | `delete_projects`      | 删除项目。                                     |
| **任务** | `create_tasks`         | 创建任务（支持智能时间识别）。                 |
|          | `update_tasks`         | 修改任务标题、内容、日期或优先级。             |
|          | `complete_tasks`       | 将任务标记为完成。                             |
|          | `delete_tasks`         | 批量删除任务。                                 |
|          | `create_subtasks`      | 为任务添加子任务。                             |
| **查询** | `query_tasks`          | 高级清单查询（支持日期范围、优先级、搜索词）。 |

## 📂 项目结构

```text
ticktick-mcp-enhanced/
├── src/
│   └── ticktick_mcp/
│       ├── __init__.py        # 包入口
│       ├── server.py          # MCP 服务入口
│       ├── auth.py            # OAuth 逻辑与回调服务器
│       ├── client_manager.py   # 客户端管理
│       ├── tools/             # 各类工具实现
│       └── utils/             # 格式化与校验工具
├── pyproject.toml            # 项目配置与依赖
└── README.md                # 本文档
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [滴答清单 Open API](https://developer.dida365.com/docs#/openapi)
- [FastMCP](https://github.com/jlowin/fastmcp)
