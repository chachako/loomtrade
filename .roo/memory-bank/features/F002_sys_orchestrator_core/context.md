# Feature Context: 系统编排 Agent 核心 (System Orchestrator Agent Core) (ID: F002_sys_orchestrator_core)
*Initialized by Feature-Lead on 2025-05-10 02:32:54*
*Last updated by Feature-Lead on 2025-05-10 02:38:43*

## 1. Overview & Goal
实现 SystemOrchestratorAgent 的核心逻辑。这包括：
1.  建立与核心 LLM (例如 GPT 系列) 的交互循环。
2.  能够解析来自用户的简单自然语言指令，并将其映射到系统可执行的操作或工具调用。
3.  通过 `F004_tool_executor_base` 功能中定义的 ToolExecutor 调用基础工具集。
4.  管理基本会话状态和上下文，以便进行连贯的对话。
目标是创建一个能够理解用户意图并协调其他系统组件以完成任务的中央控制单元。

## 2. Detailed Requirements / User Stories
*   **US1:** 作为一个用户，我希望系统编排 Agent 能够理解我用自然语言发出的简单指令，以便我能轻松地让系统执行任务。
*   **US2:** 作为一个开发者，我希望系统编排 Agent 能够与核心 LLM (例如 GPT) 建立交互，以便利用 LLM 的自然语言处理和生成能力。
*   **US3:** 作为一个开发者，我希望系统编排 Agent 能够通过 ToolExecutor 调用基础工具，以便执行具体的功能。
*   **US4:** 作为一个用户，我希望系统编排 Agent 能够管理基本的会话上下文，以便进行连贯的多轮对话。

## 3. Acceptance Criteria
*   **AC1.1 (for US1):** 给定一个简单的指令 (例如，“告诉我当前时间”)，当用户输入该指令时，那么系统编排 Agent 应能识别意图并将其映射到一个已知的系统操作 (例如，调用 `get_current_time` 工具)。
*   **AC1.2 (for US1):** 给定一个包含参数的简单指令 (例如，“搜索关于‘人工智能’的新闻”)，当用户输入该指令时，那么系统编排 Agent 应能识别意图和参数 (例如，工具 `search_news`，参数 `query='人工智能'`)。
*   **AC2.1 (for US2):** 给定系统编排 Agent 已初始化，当它需要 LLM 处理时 (例如，解析复杂指令或生成自然语言响应)，那么它应该能够成功地向配置的 LLM 发送请求并接收响应。
*   **AC3.1 (for US3):** 给定一个指令被映射到一个需要参数的工具调用 (例如，`tool_A(param1='value1')`)，当系统编排 Agent 决定执行该工具时，那么它应该能够通过 `F004_tool_executor_base` 正确调用 `tool_A` 并传递 `param1='value1'`。
*   **AC3.2 (for US3):** 给定一个工具成功执行并返回结果，当系统编排 Agent 收到结果时，那么它应该能够处理该结果 (例如，用于生成用户响应或决定下一步操作)。
*   **AC4.1 (for US4):** 给定用户在前一轮对话中提供了信息 (例如，“我最喜欢的颜色是蓝色”)，当用户在后续轮次中提出相关问题 (例如，“它是什么颜色？”) 时，那么系统编排 Agent 应能利用先前存储的上下文 (“蓝色”) 来回答。
*   **AC4.2 (for US4):** 给定一个多轮对话，当会话结束或重置时，那么相关的会话上下文应该被清除或归档。

## 4. Scope
### 4.1. In Scope:
*   实现 `SystemOrchestratorAgent` 类。
*   与一个可配置的 LLM 服务 (例如 OpenAI API) 的基本集成。
*   将简单自然语言指令解析为预定义工具调用或操作的能力。
*   通过 `ToolExecutor` (来自 F004) 调用工具的机制。
*   基本的内存机制，用于存储和检索短期会话上下文 (例如，最近几轮对话的关键信息)。
*   处理来自 LLM 和工具执行器的成功响应和基本错误。
*   定义核心的 Agent 交互循环 (接收输入 -> 处理/理解 -> 决定行动 -> 执行 -> 生成响应)。
### 4.2. Out of Scope:
*   高级自然语言理解 (NLU)，如复杂的多意图指令、情感分析等 (依赖 LLM 的能力)。
*   复杂的对话管理策略 (例如，高级错误处理、澄清式提问、主动引导对话)。
*   长期记忆或知识库的集成。
*   用户认证和授权。
*   与其他 Agent (例如 AnalystAgent, TraderAgent) 的直接交互 (这将在后续的集成功能中处理)。
*   ToolExecutor (`F004_tool_executor_base`) 本身的实现。
*   任何具体的工具实现 (例如，`search_news` 工具的实际逻辑)。
*   UI/UX 或任何前端交互逻辑。

## 5. Technical Notes / Assumptions
*   假设 `F004_tool_executor_base` 功能将提供一个清晰的接口供 `SystemOrchestratorAgent` 调用工具。
*   假设 LLM API (例如 OpenAI) 是可访问的，并且 API 密钥等配置是可用的。
*   Agent 的核心逻辑将主要用 Python 实现。
*   初步的指令到操作的映射可能基于一组预定义的关键字或简单的模式匹配，或者直接依赖 LLM 进行意图识别。
*   会话状态将暂时存储在内存中。
*   时间戳格式将遵循 YYYY-MM-DD HH:MM:SS。