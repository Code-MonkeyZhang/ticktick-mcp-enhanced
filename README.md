<p align="center">
  <img src="logo.png" width="128" alt="TickTick MCP Logo">
</p>

# 滴答清单 MCP 服务器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器，允许大语言模型管理你的滴答清单/TickTick 待办事项。

🔗 **API 文档**: [滴答清单官方 OpenAPI](https://developer.dida365.com/docs#/openapi)

---

## 🛠️ 准备工作

- **Python 3.10+**
- 已安装 [**uv**](https://github.com/astral-sh/uv) (推荐)
- 滴答清单或 TickTick 账号
- API 凭证 (Client ID, Client Secret)

## 🔑 认证设置

在 [滴答清单开发者中心](https://developer.dida365.com/manage)（国内用户）或 [TickTick Developer Center](https://developer.ticktick.com/manage) 注册一个应用。

1. 点击 **"New App"**。
2. 保存你的 **Client ID** 和 **Client Secret**。
3. 设置 **Redirect URI**：
   - **推荐使用**: `http://localhost:8000/callback`。
   - _自定义_: 如果你修改了此项，请相应地设置 `TICKTICK_REDIRECT_URI` 环境变量。

## 🚀 快速开始

### 1. 克隆代码库

```bash
git clone https://github.com/Code-MonkeyZhang/ticktick-mcp-enhanced
cd ticktick-mcp-enhanced
```

### 2. 配置 MCP 客户端

以 **Claude Desktop** (`claude_desktop_config.json`) 为例：

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--directory",
        "/项目/的/绝对路径/ticktick-mcp-enhanced",
        "ticktick-mcp",
        "run"
      ],
      "env": {
        "TICKTICK_ACCOUNT_TYPE": "china", // "china" 或 "global" 选择你滴答清单账户的区域
        "TICKTICK_CLIENT_ID": "你的_client_id",
        "TICKTICK_CLIENT_SECRET": "你的_client_secret",
        "TICKTICK_REDIRECT_URI": "http://localhost:8000/callback", // 这里填写上一步中你在开发者平台注册的URL
        "MCP_LOG_ENABLE": "false" // 可选：开启MCP日志记录功能
      }
    }
  }
}
```

### 3. 授权并使用

1. 重启你的 MCP 客户端。
2. 问 AI：“查看我今天的任务”。
3. **首次授权**：AI 将提供一个授权链接。点击链接 -> 登录 -> 将弹出一个授权页面，显示授权已完成。
4. 你可以返回 LLM 客户端并使用此 MCP 访问滴答清单。

> 你的授权 Token 将存储在项目文件夹下的 `.ticktick_token.json` 中。

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
├── ticktick_mcp/
│   ├── src/
│   │   ├── server.py          # MCP 服务入口
│   │   ├── auth.py            # OAuth 逻辑与回调服务器
│   │   ├── tools/             # 各类工具实现
│   │   └── utils/             # 格式化与校验工具
│   └── __main__.py            # CLI 启动项
├── pyproject.toml             # 项目配置与依赖
└── README_en.md               # 英文文档
```
