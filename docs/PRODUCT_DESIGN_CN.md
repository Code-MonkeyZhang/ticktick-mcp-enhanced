# TickTick MCP Enhanced - 产品设计文档 (中文版)

## 1. 愿景与目标
为 MCP 客户端提供一个无摩擦、现代化的 TickTick 集成方案。
**核心目标**：零手动配置。用户不应再需要手动执行 `git clone`、`pip install` 或运行独立的 `python auth.py` 脚本。用户只需在配置文件中填入凭证，剩下的所有工作（依赖安装、环境隔离、登录认证）都由 MCP Server 和 Agent 自动处理。

## 2. 核心理念
**"配置即安装" (Configuration is Installation)**
- 未来目标：无需手动下载源码。
- **无需手动环境配置**：用户不需要知道 `virtualenv` 或 `pip` 是什么。
- **无需独立认证脚本**：认证流程融入到工具交互中，不再是游离于主程序之外的脚本。
- **"服务优先，认证其次" (Server First, Auth Second)**：只要配置了 ID 和 Secret，服务就必须能启动。即使没有登录，服务也不应该崩溃，而是引导用户去登录。

## 3. 必需输入参数
系统应当仅依赖用户在 MCP 客户端配置文件（如 `settings.json`）中提供的以下**三个参数**运行：

1.  **Account Type** (账户类型)：`china` (对应 dida365.com/滴答清单) 或 `global` (对应 ticktick.com/国际版)。
2.  **Client ID**：从滴答清单开发者中心获取。
3.  **Client Secret**：从滴答清单开发者中心获取。

*(注：Access Token 虽然是调用 API 必需的，但应当由程序在运行时使用 ID/Secret 自动获取或引导用户获取，而不是要求用户手动填入配置。)*

## 4. 现代化架构 (UV 方案)
我们将抛弃传统的 `setup.py` 打包方式，转而采用基于 `pyproject.toml` 和 `uv` 的现代化标准。

### 4.1 项目结构
- **`pyproject.toml`**：唯一的依赖和构建配置文件。
- **依赖管理**：完全由 `uv` 动态接管。用户无需触碰 `pip`。
- **运行时**：通过 `uv run` 执行，确保每次运行都在一个纯净、隔离的环境中。

### 4.2 配置示例 (Gemini/Claude CLI)
用户的配置文件应该像这样简洁：

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

## 5. 工具集重设计与认证流程

Server 将暴露两类工具。认证过程现在完全工具化，赋予 Agent 协助用户的能力。

### 5.1 管理类工具 (新增)
这些工具允许 Agent 在无需用户干预命令行的情况下管理连接状态。

| 工具名称 | 参数 | 描述 |
| :--- | :--- | :--- |
| **`ticktick_status`** | 无 | **检查连接状态**。如果已登录，返回当前用户信息；如果未登录，返回明确的“未认证”状态。 |
| **`start_authentication`** | 无 | **开始认证**。生成并返回 OAuth 授权链接，用户需要点击该链接。 |
| **`finish_authentication`** | `code` (string) | **完成认证**。用户将网页跳转后的 Code 复制回来，Agent 调用此工具用 Code 换取 Token 并持久化保存。 |

### 5.2 业务类工具 (现有)
所有现有的任务管理工具（如 `add_task`）保持不变，但会增加**认证拦截 (Authentication Guard)** 逻辑。
- `get_project_info`, `create_tasks`, `query_tasks` 等。

### 5.3 行为与交互流程示例

**场景：用户未登录（首次运行）**
1.  **用户**: “我今天的任务有哪些？”
2.  **Agent**: 尝试调用 `query_tasks`。
3.  **MCP Server**: 检测到没有 Token 或 Token 已过期。返回错误：
    > `Error: Authentication required. Please use the 'start_authentication' tool to log in.`
4.  **Agent**: “看起来你还没有登录滴答清单。让我来帮你。” -> 自动调用 `start_authentication`。
5.  **MCP Server**: 返回：
    > `Please open this URL to authorize: https://ticktick.com/oauth/... Then copy the 'code' from the redirected URL.`
6.  **Agent**: 将链接展示给用户，并提示用户复制 Code。
7.  **用户**: 点击链接，授权，复制 Code。对 Agent 说：“Code 是 abc123xyz”。
8.  **Agent**: 调用 `finish_authentication(code="abc123xyz")`。
9.  **MCP Server**: 验证 Code，换取 Token，保存到本地文件（如 `~/.ticktick_mcp_token.json`），返回“成功”。
10. **Agent**: “登录成功！正在获取你的任务...” -> 再次调用 `query_tasks`。
11. **MCP Server**: 返回任务列表。

## 6. 实施计划 (Implementation Plan)
1.  **构建系统重构**：用 `pyproject.toml` 替换 `setup.py`。
2.  **配置与环境**：更新 `config.py`，使其优先从环境变量读取 `CLIENT_ID` 和 `SECRET`。
3.  **认证逻辑内化**：
    - 将 `authenticate.py` 的逻辑移入 `src/auth.py`。
    - 实现基于文件的 Token 持久化存储（如 `token.json`）。
    - 实现 Token 自动刷新机制。
4.  **工具实现**：在 `server.py` 中注册上述 3 个新的认证工具。
5.  **中间件/拦截器**：为所有业务工具添加认证检查装饰器，统一处理“未登录”错误。
