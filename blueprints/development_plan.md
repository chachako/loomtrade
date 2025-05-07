# 项目开发计划：AI 自动化交易 Agent

## 1. 引言

本文档为 AI 自动化交易 Agent 项目的详细开发计划安排，旨在为开发团队（包括人类工程师和 AI 编码助手）提供清晰的阶段目标、具体任务、技术实现要点以及任务间的依赖关系。它基于 `blueprints/technical_specs.md` 进行规划，并强调 UI 与功能的并行开发以及对多资产市场的早期架构支持。

## 2. 开发指导原则

* **迭代与并行：** 遵循敏捷思想，UI/UX 设计与功能开发并行推进，小步快跑，持续集成和交付。
* **用户中心：** UI 交互是关键的测试和反馈场景，尽早通过 UI 验证功能。
* **模块化与API优先：** 各组件高内聚、低耦合，后端服务通过清晰的 API 接口与前端及其他服务交互。
* **多市场架构：** 从设计初期即考虑对多种金融市场（加密货币、股票、外汇等）的适配性。
* **文档驱动与测试覆盖：** 关键模块、接口及决策需有文档，核心逻辑应有充分测试。
* **安全性：** 系统和数据安全是最高优先级。

## 3. 开发阶段与任务详解

### 阶段一：核心框架与首个市场（加密货币）MVP

**目标：** 搭建支持多市场的核心系统框架，完整实现一个选定市场（优先加密货币合约）的 Agentic Loop 自动化交易闭环，并通过可交互 UI 进行验证。

**子阶段与任务 (Sprint/主题式组织，强调并行)：**

**3.1. 基础架构与环境**
    ***任务 1.1.1:** 项目仓库初始化 (Git), CI/CD 基础配置。
        *   *技术:* Git, GitHub Actions.
    ***任务 1.1.2:** 本地开发环境 (Docker Compose: Next.js, FastAPI, PostgreSQL)。
    *   **任务 1.1.3 (并行):**
        ***后端:** 定义并初始化核心数据库 Schema (考虑多市场扩展性)。
            *   *涉及表:* `Users`, `ExchangeConfigs` (通用，含 `market_type`, `exchange_name`, `api_key_encrypted`, `secret_key_encrypted`, `passphrase_encrypted`, `permissions`), `LLMProviderConfigs`, `TraderProfiles` (基础), `TradingStrategies` (基础), `AgentInstances`, `Positions` (通用字段), `TradeOrders` (通用字段), `AgentActivityLogs`.
            **技术:* PostgreSQL, SQLAlchemy, Alembic.
        *   **前端:** 基础项目结构搭建 (Next.js, TypeScript, Magic UI 引入)。

**3.2. 用户认证与通用配置**
    ***任务 1.2.1 (后端):** 用户账户服务 (注册、登录、JWT 认证)。
        *   *API:* `/auth/register`, `/auth/login`.
    ***任务 1.2.2 (前端):** 用户注册、登录页面及交互逻辑。
        *   *集成:* 调用任务 1.2.1 API。
    ***任务 1.2.3 (后端):** LLM Provider 配置服务 (CRUD, API Key 加密存储)。
        *   *API:* `/configs/llm`.
    ***任务 1.2.4 (前端):** LLM Provider 配置管理 UI。
        *   *集成:* 调用任务 1.2.3 API.
    ***任务 1.2.5 (后端):** 交易市场配置服务 (`ExchangeConfigs` CRUD, API Key 加密, 连通性测试框架 - 初始支持加密货币)。
        *   *设计:* 考虑不同市场 API Key 结构差异。
        **API:* `/configs/exchanges`.
    *   **任务 1.2.6 (前端):** 交易市场配置管理 UI (选择市场类型、输入凭证、测试连接)。
        *   *集成:* 调用任务 1.2.5 API.

**3.3. Agent 核心与 LLM 集成**
    ***任务 1.3.1 (后端):** Agent 核心服务框架 (FastAPI: Agent 实例管理, Agentic Loop 基础)。
    *   **任务 1.3.2 (后端):** 动态 Prompt 构建模块 (System Prompt 基础, 对话历史, 上下文注入)。
    ***任务 1.3.3 (后端):** LLM API 交互模块 (支持1-2个 LLM, 流式响应处理)。
    *   **任务 1.3.4 (后端):** LLM 响应解析器 (文本回复, 结构化工具调用 - XML/JSON)。
    ***任务 1.3.5 (并行 前/后):**
        *   **后端:** WebSocket 服务基础 (FastAPI WebSockets, 用于 Agent 消息双向通信)。
        ***前端:** WebSocket 客户端连接与基础消息处理。
    *   **任务 1.3.6 (前端):** Agent 聊天交互基础 UI (用户输入框, Agent 消息展示区)。
        *   *集成:* 任务 1.3.5。

**3.4. MVP 工具集 (加密货币市场优先，架构支持多市场)**
    ***任务 1.4.1 (后端):** 工具执行器框架 (ToolExecutor) 及市场分发机制。
        *   *设计:* 根据工具调用中的 `market_type` 分发到相应市场处理器。
    ***任务 1.4.2 (后端):** 市场数据工具 - `get_historical_klines`。
        *   *参数:* `symbol`, `market_type`, `interval`, `limit`.
        **实现:* 加密货币市场处理器 (1-2个交易所 API)。
        *   *API (内部):* Agent Core 调用。
    ***任务 1.4.3 (后端):** 市场数据工具 - `get_current_ticker_info`。
        *   *参数:* `symbols`, `market_type`.
        **实现:* 加密货币市场处理器。
    *   **任务 1.4.4 (后端):** 技术指标工具 - `calculate_indicator` (通用，输入 K线数据)。
        **参数:* `indicator_name`, `klines_data`, `parameters`.
        *   *实现:* RSI, MA/EMA (集成 TA-Lib/pandas-ta)。
    ***任务 1.4.5 (后端):** 账户工具 - `get_account_balance`。
        *   *参数:* `exchange_config_id` (隐式包含 `market_type`)。
        **实现:* 加密货币市场处理器。
    *   **任务 1.4.6 (前端):** 仪表盘资产概览 UI。
        **API 依赖:* 需要后端提供 `/account/balance` 接口 (包装任务 1.4.5)。
    *   **任务 1.4.7 (后端):** 账户工具 - `get_open_positions`。
        **参数:* `exchange_config_id`, `symbol` (optional).
        *   *实现:* 加密货币市场处理器。
    ***任务 1.4.8 (前端):** 仪表盘当前持仓列表 UI。
        *   *API 依赖:* 需要后端提供 `/positions` 接口 (包装任务 1.4.7)。
        **集成:* WebSocket 实时更新。
    *   **任务 1.4.9 (后端):** 订单工具 - `create_order`。
        **参数:* `exchange_config_id`, `symbol`, `market_type`, `side`, `type`, `amount`, `price` (opt), `leverage` (opt), `reduce_only` (opt), etc.
        *   *实现:* 加密货币市场处理器 (市价、限价单); 订单管理服务基础; `TradeOrders`, `Positions` 表更新。
    ***任务 1.4.10 (后端):** 订单工具 - `close_position` (市价平仓)。
        *   *实现:* 加密货币市场处理器 (本质是反向 `create_order`)。
    ***任务 1.4.11 (后端):** 订单工具 - `set_position_tp_sl` (为现有加密货币持仓设置)。
    *   **任务 1.4.12 (前端):** 交易历史 UI, 订单管理 UI (取消订单等)。
        **API 依赖:* 需要后端提供 `/orders/history`, `/orders/open`, `/orders/{id}/cancel` 等接口。
    *   **任务 1.4.13 (后端):** LLM 辅助工具 - `ask_user_clarification`。
        *   *实现:* 通过 WebSocket 推送问题到前端 Agent 聊天。

**3.5. 策略定义与 Agent 执行 (MVP - 加密货币)**
    ***任务 1.5.1 (后端):** 预设交易风格 (Trader Profile) 服务与管理。
    *   **任务 1.5.2 (前端):** 交易风格选择 UI。
    ***任务 1.5.3 (后端):** 交易策略服务 (CRUD, 结构化规则存储 - 初始支持 RSI/MA 条件, TP/SL)。
    *   **任务 1.5.4 (前端):** 结构化策略构建 UI (针对加密货币的RSI/MA条件, TP/SL)。
        **集成:* 调用任务 1.5.3 API。
    *   **任务 1.5.5 (后端):** Agent 核心逻辑实现策略加载与执行 (基于选定市场的结构化规则)。
        **触发:* 定时轮询 (简化版)。
        *   *集成:* 所有 MVP 工具集。
    ***任务 1.5.6 (前端):** TradingView 图表嵌入，并标记 Agent 开平仓点。
        *   *数据来源:* WebSocket 或轮询 `/positions`, `/orders/history`.
    ***任务 1.5.7 (并行 前/后):** Agent 状态与活动日志。
        *   **后端:** `AgentActivityLogs` 记录核心决策与工具调用。
        *   **前端:** Agent 思考日志/活动日志基础展示 UI (通过 WebSocket 接收)。

**3.6. 风险控制与部署 (MVP)**
    ***任务 1.6.1 (后端):** 实现基础风险控制 (最大仓位限制 - 在 `create_order` 中校验)。
    *   **任务 1.6.2 (文档):** 编写 MVP 用户操作指南和风险提示。
    ***任务 1.6.3 (测试):** 核心功能 E2E 测试 (UI 驱动部分场景)。
    *   **任务 1.6.4 (部署):** MVP 版本部署到测试/预生产环境 (Docker)。
    *   **任务 1.6.5 (反馈):** 内部团队试用与反馈收集。

---

### 阶段二：功能增强与多市场扩展

**目标：** 优化体验，增强策略能力，初步支持第二类金融市场（如股票），完善通知与风险管理。

**子阶段与任务 (部分示例)：**

**3.7. 多市场支持扩展 (如股票)**
    ***任务 2.1.1 (后端):** 针对股票市场的 `ExchangeConfigs` 适配与凭证管理。
    *   **任务 2.1.2 (后端):** 实现股票市场处理器 (handler) 用于核心工具集:
        *`get_historical_klines` (股票数据源 API 集成)
        *   `get_current_ticker_info` (股票)
        *`get_account_balance` (股票经纪商)
        *   `get_open_positions` (股票)
        *`create_order` (股票: 买卖股数, 市价/限价)
        *   `close_position` (股票)
    ***任务 2.1.3 (前端):** UI 适配股票市场 (交易对选择、订单参数、数据显示等)。
    *   **任务 2.1.4 (文档):** 更新工具文档，包含股票市场参数和行为。

**3.8. 策略与 Agent 增强**
    ***任务 2.2.1 (后端):** `calculate_indicator` 工具扩展 (更多指标)。
    *   **任务 2.2.2 (后端):** 灵活策略条件组合 (AND/OR/NOT) 的后端解析与执行。
    ***任务 2.2.3 (前端):** UI 支持更复杂的策略条件构建。
    *   **任务 2.2.4 (后端):** `scan_market_opportunities` 工具实现 (支持加密和股票)。
    ***任务 2.2.5 (并行 前/后):** "Agent 思考日志" 功能完善 (更详细的流式展示)。
    *   **任务 2.2.6 (研究/实现):** 自然语言策略定义器 (初步，LLM 解析 NL 到结构化规则)。

**3.9. 用户体验与通知**
    ***任务 2.3.1 (UI/UX):** 整体审查与改进。
    *   **任务 2.3.2 (并行 前/后):** 交易分析报告模块 (基础版)。
    ***任务 2.3.3 (并行 前/后):** 通知服务 (邮件/站内信: 交易执行、风险警告)。
    *   **任务 2.3.4 (国际化):** 前后端 i18n 实现。

**3.10. 风险管理强化**
    ***任务 2.4.1 (后端):** 用户可配置的全局/策略级风险参数 (如每日最大亏损)。
    *   **任务 2.4.2 (前端):** 风险参数配置 UI。
    *   **任务 2.4.3 (并行 前/后):** “紧急停止”功能。

---

### 阶段三：高级功能与智能进化

**目标：** 引入 Agent 学习机制，提供高级分析工具，支持更复杂的交易场景。


* **策略回测引擎 (前后端并行)**
* **Agent 学习与进化 (数据库驱动的记忆 - 后端核心，前端辅助展示/反馈)**
  * `self_reflect_on_last_trade` (工具与后端逻辑)
  * `get_database_schema`, `query_database` (工具与后端逻辑)
  * Agent 核心集成记忆检索与应用
  * 参数自适应、模式识别、用户反馈增强 (研究与实现)
* **高级 NLP 与组合策略 (研究与实现)**
* **(远期) 社区、移动端等。**

## 4. 持续关注

* 性能、安全、可扩展性、文档、测试。