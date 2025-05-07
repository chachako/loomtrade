# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon `./blueprints/project_bible.md` (located in the project root directory, if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-05-07 20:22:22 - Log of updates made will be appended as footnotes to the end of this file.

*

## Project Goal

* **使命：** 赋予交易者通过自然语言驱动的 AI Agent 实现个性化、自动化的**多资产（包括加密货币、股票、外汇等）**交易能力。
* **核心问题：** 降低复杂交易策略的自动化门槛，利用 LLM 的理解与推理能力处理市场动态，并提供透明、可控的自动化交易执行。

## Key Features

* 用户通过前端定义意图
* 后端 Agent 核心协调 LLM 与工具
* LLM 规划并指导工具执行
* 工具与交易所/数据源交互
* 结果反馈形成闭环
* 支持多资产交易 (加密货币, 股票, 外汇等)
* 自然语言驱动的 AI Agent
* 个性化、自动化的交易能力
* 透明、可控的自动化交易执行

## Overall Architecture

* **基本模式：** 用户通过前端定义意图 -> 后端 Agent 核心协调 LLM 与工具 -> LLM 规划并指导工具执行 -> 工具与交易所/数据源交互 -> 结果反馈形成闭环。
* **主要服务模块：**
  * **Frontend (Next.js with React 19, Magic UI):** 用户界面、BFF API 路由。
  * **Backend (Python - FastAPI):** Agent 核心逻辑、LLM 通信、工具执行器、API 服务（需支持 i18n）、WebSocket 服务。
  * **Database (PostgreSQL):** 持久化用户数据、配置、交易历史、Agent 状态与记忆。
  * **LLM Provider:** 外部大语言模型服务。
  * **市场接口 (Market Interfaces):** 外部交易所/经纪商 API。
