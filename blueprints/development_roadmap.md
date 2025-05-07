# Vibetrade 项目开发路线图

**核心原则：** 迭代开发，尽早验证核心功能，逐步完善。每个阶段的产出都应该是可测试、可演示的。

## Phase 0: 项目基础与核心后端搭建

*   **目标：** 建立稳固的后端基础和核心 Agent 框架。
*   **主要任务：**
    1.  **环境与工具准备：**
        *   代码仓库初始化 (Git)。
        *   选择并配置项目管理/协作工具。
        *   搭建本地开发环境 (Docker Compose 配置：Next.js, FastAPI, PostgreSQL)。
    2.  **数据库设计与实现：**
        *   根据 `blueprints/technical_specs.md` 中的数据模型，创建 PostgreSQL 数据库表结构（需考虑多资产通用性，如 `symbol` 替代 `pair`）。
        *   实现基础的 CRUD 操作接口 (可以使用 SQLAlchemy 或类似 ORM)。
    3.  **FastAPI 主后端服务搭建：**
        *   初始化 FastAPI 项目。
        *   实现用户账户服务基础：用户注册、登录接口，JWT 或其他方式的认证机制。
        *   实现**市场连接凭据 (API Key/Secret等)** 和 LLM Provider 配置的安全存储与管理接口（需支持不同类型市场的凭据）。
        *   考虑后端 API 的初步 i18n 支持框架。
    4.  **Agent 核心逻辑框架：**
        *   在 FastAPI 后端搭建 Agent Core 基础框架。
        *   实现 Agentic Loop 的基本骨架（此时 LLM 交互可为 mock 或简化版）。
        *   设计工具执行器的基本接口和注册机制，使其易于扩展以支持不同市场的工具。
    5.  **基础工具实现 (后端 - 针对首个目标市场，如加密货币)：**
        *   实现 `get_account_balance` 工具 (支持 `account_id`)。
        *   实现 `get_historical_klines` 工具 (支持 `symbol`, `market_type`) 以连接至少一个市场接口获取数据。
*   **产出物：**
    *   可运行的 FastAPI 后端服务，提供用户认证和配置管理 API（支持多市场凭据类型）。
    *   包含核心表结构的数据库（设计具有一定通用性）。
    *   Agent Core 的初步框架，工具执行器接口已考虑扩展性。
    *   能够从至少一个市场获取K线数据和账户余额的后端能力。

## Phase 1: MVP - 前端应用骨架与基本用户交互

*   **目标：** 搭建 Next.js (React 19) 前端应用，集成 Magic UI 和 i18n，实现用户登录、基本配置界面和仪表盘的初步展示。
*   **主要任务：**
    1.  **Next.js 前端项目初始化：**
        *   创建 Next.js (React 19) 项目，配置 TypeScript, ESLint, Prettier, **Magic UI**, **next-i18next**。
        *   根据 `blueprints/technical_specs.md` 规划项目目录结构。
    2.  **用户引导与初始配置 UI：**
        *   实现用户注册、登录页面。
        *   实现**市场连接凭据**配置和 LLM Provider 配置的表单和交互逻辑 (调用 Phase 0 的后端 API)。
        *   实现交易偏好/风格的初步选择界面。
    3.  **主仪表盘 (Dashboard) UI 骨架：**
        *   搭建仪表盘三栏式或模块化布局。
        *   实现资产概览、当前持仓（空状态或 mock 数据）、当前委托（空状态或 mock 数据）的静态展示组件。
        *   集成 TradingView Lightweight Charts™ 并展示 mock K线数据或通过后端获取的K线数据。
    4.  **Next.js API Routes (BFF) 实现：**
        *   为前端认证、会话管理提供 BFF API。
        *   代理部分对主后端服务的请求。
    5.  **WebSocket 客户端集成 (初步)：**
        *   在 Next.js 前端设置 WebSocket 客户端连接到 FastAPI 后端 (此时后端 WebSocket 服务可为简单 echo 或广播 mock 数据)。
*   **产出物：**
    *   用户可以注册、登录的 Next.js Web 应用。
    *   用户可以配置**市场连接凭据**和 LLM API Key。
    *   初步的仪表盘界面，能展示静态或 mock 的市场数据和图表。

## Phase 2: MVP - Agent 核心交易功能与策略执行

*   **目标：** 实现 Agent 的核心交易能力和基于简单规则的策略执行（针对首个目标市场）。
*   **主要任务：**
    1.  **核心交易工具实现 (后端 - FastAPI & ToolExecutor)：**
        *   `get_open_positions` (支持 `symbol`, `market_type`)
        *   `create_order` (市价单、限价单，支持 `symbol`, `market_type`, `amount` 需明确含义)
        *   `close_position` (支持 `symbol`, `market_type`)
        *   `set_position_tp_sl` (支持 `symbol`, `market_type`)
        *   `calculate_indicator` (至少支持 RSI, MA，确保能处理不同来源的K线数据)
    2.  **Agent 核心逻辑增强 (后端 - FastAPI Agent Core)：**
        *   集成 LLM API 调用，用于解析简单的、结构化的策略指令（需考虑指令对不同市场参数的适配）。
        *   Agent 能够根据解析后的策略调用相应市场的工具执行交易。
        *   Agent 状态管理（运行中、暂停等）。
    3.  **策略配置 UI (前端 - Next.js)：**
        *   提供结构化的 UI 界面，允许用户定义基于简单指标的入场、出场条件（UI需考虑不同市场指标和参数的差异性）。
        *   保存策略到后端。
    4.  **仪表盘功能增强 (前端 - Next.js)：**
        *   实时展示真实的持仓信息、订单状态（通过 WebSocket）。
        *   在 TradingView 图表上标记 Agent 的开平仓点位。
        *   提供手动平仓、修改止损/止盈的交互。
    5.  **WebSocket 服务增强 (后端 - FastAPI)：**
        *   推送真实的持仓、订单、Agent 状态更新到前端。
*   **产出物：**
    *   用户可以通过结构化界面定义简单交易策略（针对首个目标市场）。
    *   Agent 能够根据策略执行基本的自动化交易（针对首个目标市场）。
    *   仪表盘能实时反映 Agent 的交易活动和账户状态。

## Phase 3: MVP - “Agent思考日志”、NLU 初步集成与 MVP 收尾

*   **目标：** 实现核心的透明度功能，初步集成自然语言策略，完成 MVP 定义的所有核心功能。
*   **主要任务：**
    1.  **Agent 思考日志 (后端 & 前端)：**
        *   后端 Agent Core 产生日志。
        *   通过 WebSocket 将日志流式推送到前端。
        *   前端实现“Agent 思考日志” Tab 页，实时流式展示。
    2.  **自然语言策略定义器 (初步)：**
        *   前端提供自然语言输入框。
        *   后端 Agent (LLM) 尝试解析特定模式或简化版的自然语言策略（能区分不同市场的意图，如“买入股票AAPL” vs “做多BTC合约”）。
    3.  **与 Agent 对话 (Chat with Agent) 初步功能：**
        *   前端实现聊天界面。
        *   Agent (LLM) 能够响应简单的查询指令。
    4.  **风险控制与安全：**
        *   实现 MVP 范围内的基本风险控制。
        *   确保 API Key 等敏感信息的加密存储和安全使用。
    5.  **测试、文档与部署准备：**
        *   单元测试、集成测试。
        *   编写用户文档和开发者文档初稿。
        *   准备 MVP 版本的部署。
*   **产出物：**
    *   功能完整的 Vibetrade MVP 版本（针对首个目标市场）。
    *   用户可以体验到 Agent 的思考过程。
    *   可以尝试使用自然语言（简化版）定义策略。

## Phase 4 onwards: V1.x 及后续迭代 (持续进行)

*   **目标：** 根据 `blueprints/technical_specs.md` 中的 V1.x 和 V2.0 规划，持续增强功能，并逐步扩展多资产支持。
*   **主要方向：**
    *   **增强策略定义：** 更丰富的指标支持（适配多市场），更灵活的逻辑组合，动态**交易标的**扫描与选择逻辑（支持按市场类型筛选）。
    *   **增强用户体验：** UI/UX 优化（Magic UI 深入应用），交易分析报告（区分不同市场特性）。
    *   **增强风险管理：** 用户可配置的全局和策略级风险参数（考虑不同市场的风险模型）。
    *   **Agent 学习与进化：** 实现交易反思机制 (`self_reflect_on_last_trade`，反思需包含市场类型和标的），构建数据库驱动的长期记忆。
    *   **扩展对其他资产类别的支持：** 逐步增加对股票、外汇等市场的完整工具链和策略支持。
    *   **通知系统。**
    *   **策略回测引擎 (V2.0 - 支持多资产回测)。**