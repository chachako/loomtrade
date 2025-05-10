# Feature Context: 核心工具执行器与基础工具集 (Tool Executor & Base Toolset) (ID: F004_tool_executor_base)
*Initialized by Feature-Lead on 2025-05-10 06:04:55*
*Updated by Feature-Lead on 2025-05-10 06:06:07*

## 1. Overview & Goal
本功能的核心目标是构建 ToolExecutor 模块以及一套基础的、MVP 必需的工具集。
ToolExecutor 模块需要能够：
1.  安全地解析符合预定义 XML 格式的工具调用请求。
2.  根据解析出的工具名称和参数，动态调用相应的工具实现。
3.  处理工具执行的成功或失败，并返回结构化的结果。
基础工具集应至少包括：
1.  市场数据获取工具：例如，获取最新的 K 线数据、订单簿深度、实时价格等（需与 `F005_binance_connector` 协同）。
2.  技术指标计算工具：例如，计算常用的技术指标如 MA, EMA, RSI, MACD 等。
该模块是 Agent 与外部世界交互和执行具体操作的基础。

## 2. Detailed Requirements / User Stories
*   作为一个 Analyst Agent，我希望能够调用 ToolExecutor 来获取指定交易对的最新 K 线数据，以便进行市场分析。
*   作为一个 Analyst Agent，我希望能够调用 ToolExecutor 来计算指定交易对和时间周期的移动平均线 (MA)，以便识别趋势。
*   作为一个 Trader Agent，我希望能够调用 ToolExecutor 来获取指定交易对的当前订单簿深度，以便评估市场流动性。
*   作为一个 System Orchestrator，我希望 ToolExecutor 能够准确解析 XML 格式的工具调用请求，并路由到正确的工具实现，以便可靠地执行 Agent 的指令。
*   作为一个 Developer，我希望 ToolExecutor 提供清晰的错误处理机制和结构化的结果返回，以便于调试和集成。

## 3. Acceptance Criteria
*   **ToolExecutor - XML 解析:**
    *   Given 一个符合预定义 XML 模式的工具调用请求 (例如 `<tool_name><param1>value1</param1></tool_name>`)
    *   When ToolExecutor 接收到该请求
    *   Then ToolExecutor 能够成功解析出工具名称和所有参数及其对应的值。
    *   Given 一个不符合 XML 模式的工具调用请求 (例如，标签未闭合，参数格式错误)
    *   When ToolExecutor 接收到该请求
    *   Then ToolExecutor 返回一个明确的解析错误，并指明错误原因。
*   **ToolExecutor - 动态调用:**
    *   Given 一个已注册的工具名称和合法的参数
    *   When ToolExecutor 解析并尝试调用该工具
    *   Then 对应的工具实现被成功调用。
    *   Given 一个未注册的工具名称
    *   When ToolExecutor 尝试调用该工具
    *   Then ToolExecutor 返回一个明确的“工具未找到”错误。
*   **ToolExecutor - 结果返回:**
    *   Given 一个工具成功执行
    *   When ToolExecutor 完成工具调用
    *   Then ToolExecutor 返回一个结构化的成功结果，包含工具的输出。
    *   Given 一个工具执行失败 (例如，内部错误，依赖服务不可用)
    *   When ToolExecutor 完成工具调用
    *   Then ToolExecutor 返回一个结构化的失败结果，包含错误信息和类型。
*   **市场数据工具 - K 线数据:**
    *   Given 一个交易对 (例如 `BTC/USDT`)，一个时间周期 (例如 `1h`)，以及一个数量 (例如 `100`)
    *   When 调用“获取 K 线数据”工具
    *   Then 返回包含最近 100 条 1 小时 K 线数据（开盘价，最高价，最低价，收盘价，成交量，时间戳）的列表。
    *   (需与 `F005_binance_connector` 协同，错误处理应考虑连接器可能发生的错误)
*   **技术指标工具 - MA 计算:**
    *   Given 一系列 K 线数据 (例如，收盘价列表) 和一个周期 (例如 `20`)
    *   When 调用“计算 MA”工具
    *   Then 返回一个包含对应周期 MA 值的列表。

## 4. Scope
### 4.1. In Scope:
*   ToolExecutor 核心模块的 XML 解析、动态调度、结果处理逻辑。
*   基础市场数据获取工具：获取 K 线数据，获取订单簿深度，获取实时价格。
*   基础技术指标计算工具：MA, EMA, RSI, MACD。
*   为上述工具定义清晰的输入参数和输出结构。
*   基本的错误处理和日志记录。
### 4.2. Out of Scope:
*   `F005_binance_connector` 的实现 (ToolExecutor 仅作为其使用者)。
*   复杂的错误重试逻辑或熔断机制 (MVP 阶段简化)。
*   高级技术指标或自定义指标的计算。
*   工具的权限管理或配额限制 (MVP 阶段简化)。
*   图形化工具管理界面。

## 5. Technical Notes / Assumptions
*   ToolExecutor 将接收符合特定 XML 模式的字符串作为输入。
*   工具的实现将是可插拔的，ToolExecutor 通过配置或注册表发现和调用工具。
*   市场数据工具将依赖 `F005_binance_connector` 模块提供原始数据。
*   技术指标计算工具将接收结构化的市场数据作为输入。
*   所有工具的执行都应是无状态的，或者其状态管理与 ToolExecutor 解耦。
*   返回结果将采用结构化格式 (例如 JSON 或 Python 字典)。
*   错误代码和消息将标准化，以便于上层模块处理。