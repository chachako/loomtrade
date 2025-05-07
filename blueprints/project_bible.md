# Project Bible: AI 自动化交易 Agent 核心技术纲要

**本文档定位：** 为项目团队成员提供核心技术架构、关键决策及其背后逻辑的快速概览，作为日常开发和新人理解项目的统一技术认知起点。它是 `blueprints/technical_specs.md` 的高度浓缩和索引，旨在快速回顾而非详尽解释。

## 1. 项目使命与核心解决的问题

*   **使命：** 赋予交易者通过自然语言驱动的 AI Agent 实现个性化、自动化的**多资产（包括加密货币、股票、外汇等）**交易能力。
*   **核心问题：** 降低复杂交易策略的自动化门槛，利用 LLM 的理解与推理能力处理市场动态，并提供透明、可控的自动化交易执行。

## 2. 核心架构概览

*   **基本模式：** 用户通过前端定义意图 -> 后端 Agent 核心协调 LLM 与工具 -> LLM 规划并指导工具执行 -> 工具与交易所/数据源交互 -> 结果反馈形成闭环。
*   **主要服务模块：**
    *   **Frontend (Next.js with React 19, Magic UI):** 用户界面、BFF API 路由。
    *   **Backend (Python - FastAPI):** Agent 核心逻辑、LLM 通信、工具执行器、API 服务（需支持 i18n）、WebSocket 服务。
    *   **Database (PostgreSQL):** 持久化用户数据、配置、交易历史、Agent 状态与记忆。
    *   **LLM Provider:** 外部大语言模型服务。
    *   **市场接口 (Market Interfaces):** 外部交易所/经纪商 API。

## 3. 技术选型

*   **Frontend:** Next.js (React 19), Magic UI, TypeScript.
    *   **国际化 (i18n):** 计划使用 `next-i18next` 或适用于 React 19 的社区最佳实践方案。
*   **Backend:** Python (FastAPI), SQLAlchemy (ORM).
    *   **国际化 (i18n):** API 返回的错误消息、状态文本等需支持多语言 (具体库待定，如 `python-i18n` 或 FastAPI 中间件方案)。
*   **Database:** PostgreSQL.
*   **LLM 交互模式:** Agentic Loop (Tool-Using LLM).
*   **图表库:** TradingView Lightweight Charts™ / Trading Platform (需评估多资产类别适用性).

## 4. 关键设计决策与核心机制

*   **Agentic Loop 核心阶段:** (输入处理 -> Prompt 构建 -> LLM 交互 -> 响应解析 -> 工具执行 -> 结果处理 -> 循环/行动)
*   **工具 (Tools) 设计原则:** 原子性, 结构化 I/O, 明确规范。
*   **Prompt 工程核心要素:** System Prompt, 对话历史, 当前任务/上下文输入。
*   **状态管理与数据库驱动的记忆机制:** 三层记忆思想 (短期/中期/长期), 核心是数据库驱动，通过交易反思 (`self_reflect_on_last_trade`) 积累经验。
*   **LLM "幻觉"缓解策略:** 严格校验, 边界清晰, 用户确认, LLM 不直接执行高风险操作, 日志监控。

## 5. 核心数据模型 (概览)

*   **关键表:** `Users`, `ExchangeAPIKeys`, `LLMProviderConfigs`, `TraderProfiles`, `TradingStrategies`, `AgentInstances`, `Positions`, `TradeOrders`, `TradeReflections` (核心学习表), `AgentActivityLogs`, `AgentBeliefs`.
*(注：详细字段请参考 `blueprints/technical_specs.md`)*

## 6. 开发与部署要点

*   **开发环境:** Docker Compose (统一管理 Next.js, FastAPI, PostgreSQL)。
*   **部署策略:**
    *   **服务器部署:** Docker 容器部署到云平台或自建服务器，通过域名访问 (Vercel 是 Next.js 首选)。
    *   **本地化运行 (可选/未来):** 探索打包成本地二进制文件 (如 Electron/Tauri)。
    *   **独立扩展:** 前后端服务可独立部署和扩展。

## 7. 核心工具类别 (示例)

*   **市场数据:** `get_historical_klines` (获取指定 `symbol` 的K线), `get_current_ticker_info` (获取指定 `symbols` 的行情), `scan_market_opportunities` (按 `market_type` 扫描市场).
*   **技术指标:** `calculate_indicator` (通用指标计算).
*   **账户与订单:** `get_account_balance` (区分 `account_id`), `get_open_positions` (按 `symbol`), `create_order` (需指定 `symbol`, `market_type`, `amount` 含义需明确), `cancel_order`, `close_position` (按 `symbol`), `set_position_tp_sl`.
*   **LLM 辅助:** `ask_user_clarification`.
*   **内部状态与记忆:** `update_internal_belief_state`, `log_agent_activity`, `self_reflect_on_last_trade`.
*   **数据库交互 (记忆核心):** `get_database_schema`, `query_database`.

---
*本文档旨在提供核心技术与架构的快速参考，详情请务必查阅 `blueprints/technical_specs.md`。*