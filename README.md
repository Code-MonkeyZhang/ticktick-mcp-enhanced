<p align="center">
  <img src="logo.png" width="128" alt="TickTick MCP Logo">
</p>

# 滴答清单 MCP 服务器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器，允许大语言模型管理你的滴答清单/TickTick 待办事项。

🔗 **API 文档**: [滴答清单官方 OpenAPI](https://developer.dida365.com/docs#/openapi)

---

## ✨ 功能特性

- **🤖 让 AI Agent 管理你的任务**：通过自然语言指令创建、查询、更新和完成任务
- **🔑 OAuth 2.0 安全认证**：使用标准的 OAuth 2.0 流程，支持滴答清单国际版和国内版
- **📅 智能任务管理**：支持创建任务、项目、子任务，以及复杂的查询功能
- **⏰ 时间识别**：自动识别自然语言中的时间描述（如"明天"、"下周"）
- **🔍 高级查询**：按日期范围、优先级、关键词等多维度筛选任务

## 🛠️ 前置条件

- **操作系统**：macOS 或 Windows
- **Python 版本**：3.10 或更高
  - macOS：通常自带，运行 `python3 --version` 检查
  - Windows：从 [python.org](https://www.python.org/downloads/) 下载安装
- **滴答清单账号**（国际版或国内版）
- **LLM 客户端**（如 Claude Desktop、OpenCode 等）

## 🔑 获取 API 凭证

在 [滴答清单开发者中心](https://developer.dida365.com/manage)（国内用户）或 [TickTick Developer Center](https://developer.ticktick.com/manage) 注册一个应用。

1. 点击 **"New App"**。
2. 保存你的 **Client ID** 和 **Client Secret**。
3. 设置 **Redirect URI**：
   - **推荐使用**: `http://localhost:8000/callback`。
   - _自定义_: 如果你修改了此项，请相应地设置 `TICKTICK_REDIRECT_URI` 环境变量。

## 🚀 安装与使用

### 1. 安装 uv 包管理器（如果未安装）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目并创建虚拟环境

```bash
# 克隆项目
git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced.git
cd ticktick-mcp-enhanced

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 安装项目（可编辑模式）
uv pip install -e .
```

### 3. 配置 LLM 客户端

#### Claude Desktop

找到配置文件：

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "ticktick": {
      "command": ["/绝对路径/到/ticktick-mcp-enhanced/.venv/bin/ticktick-mcp"],
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

> **重要**：
> - 将 `/绝对路径/到/ticktick-mcp-enhanced` 替换为项目的实际绝对路径
> - Windows 用户请使用双反斜杠 `\\` 或正斜杠 `/`
> - `TICKTICK_ACCOUNT_TYPE`：国内用户填 `"china"`，国际用户填 `"global"`

#### 开启日志（可选）

如需调试，可在配置中添加环境变量：

```json
{
  "mcpServers": {
    "ticktick": {
      "command": ["/绝对路径/到/ticktick-mcp-enhanced/.venv/bin/ticktick-mcp"],
      "env": {
        "TICKTICK_ACCOUNT_TYPE": "china",
        "TICKTICK_CLIENT_ID": "你的_client_id",
        "TICKTICK_CLIENT_SECRET": "你的_client_secret",
        "TICKTICK_REDIRECT_URI": "http://localhost:8000/callback",
        "MCP_LOG_ENABLE": "true"
      }
    }
  }
}
```

**日志说明：**

- **默认状态**：日志功能默认关闭
- **开启后**：日志会以 `session_YYYYMMDD_HHMMSS.log` 的格式保存在项目根目录的 `logs/` 文件夹中
- **注意**：所有日志仅写入文件，**绝不会**输出到终端，避免干扰 MCP 协议

### 4. 授权并使用

1. **重启 LLM 客户端**（如 Claude Desktop）
2. **首次授权**：
   - 在对话中输入："帮我开始认证滴答清单"
   - AI 会调用 `start_authentication` 工具，返回一个授权链接
   - 点击链接 -> 登录滴答清单 -> 授权成功后自动跳转到本地回调页面
   - 关闭浏览器窗口，返回 LLM 客户端

3. **开始使用**
   - 查看任务："查看我今天的任务"
   - 创建任务："创建一个任务：明天下午3点开会"
   - 查询项目："查看所有清单"
   - 完成任务："标记第一个任务为完成"

> **注意**：你的授权 Token 将存储在项目文件夹下的 `.ticktick_token.json` 中，请勿泄露。

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

## 🔧 开发指南

### 运行测试

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 运行测试（如果有）
pytest tests/
```

### 构建分发包

```bash
# 构建
python -m build

# 分发包位于 dist/ 目录
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [滴答清单 Open API](https://developer.dida365.com/docs#/openapi)
- [FastMCP](https://github.com/jlowin/fastmcp)
