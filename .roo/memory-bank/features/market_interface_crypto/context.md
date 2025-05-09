# Feature Context: Cryptocurrency Market Interface (ID: market_interface_crypto)
*Initialized by Feature-Lead on 2025-05-09 18:53:25, Updated on 2025-05-09 18:55:01*

## 1. Overview & Goal
负责设计和实现与主流加密货币交易所 API 的集成。**MVP 阶段将首先支持 Binance (币安) 的合约交易 (USDⓈ-M Futures)，后续可考虑扩展至 OKX。**
此模块需要封装以下核心功能：
1.  获取市场数据：历史K线 (OHLCV)，实时行情 Ticker，订单簿深度。
2.  订单执行：创建市价单、限价单，取消订单。
3.  账户管理：查询账户余额、当前持仓详情、杠杆和保证金模式。
4.  错误处理：统一处理交易所特定的 API 错误码和消息，进行适当的重试或向调用方报告。
5.  速率限制管理：遵守交易所的 API 调用频率限制。
目标是为 Agent 核心和工具执行器提供一套稳定、可靠且接口尽可能一致的加密货币市场交互层。
核心技术栈为 Python。

## 2. Detailed Requirements / User Stories

### 2.1 Market Data (Binance USDⓈ-M Futures)
*   **US-MD-001:** 作为 Agent，我希望能够获取指定交易对（如 BTCUSDT）在特定时间周期（如 1h, 4h, 1d）的历史K线数据 (OHLCV)，以便进行技术分析。
*   **US-MD-002:** 作为 Agent，我希望能够获取一个或多个指定交易对的最新实时行情 Ticker 信息（如最新价、24h涨跌幅），以便快速了解市场动态。
*   **US-MD-003:** 作为 Agent，我希望能够获取指定交易对的当前订单簿深度信息（买卖盘），以便评估市场流动性。

### 2.2 Order Execution (Binance USDⓈ-M Futures)
*   **US-OE-001:** 作为 Agent，我希望能够为指定交易对创建市价单（买入/卖出），以便快速执行交易。
*   **US-OE-002:** 作为 Agent，我希望能够为指定交易对创建限价单（买入/卖出），并能指定价格和数量，以便在特定价位执行交易。
*   **US-OE-003:** 作为 Agent，我希望能够取消一个尚未成交的订单，以便调整交易策略。
*   **US-OE-004:** 作为 Agent，我希望能够查询特定订单的详细状态（如是否成交、成交均价、成交数量），以便跟踪订单执行情况。
*   **US-OE-005:** 作为 Agent，我希望能够为指定交易对的持仓设置止盈单和止损单（例如，使用 `STOP_MARKET` 或 `TAKE_PROFIT_MARKET` 类型的订单）。

### 2.3 Account Management (Binance USDⓈ-M Futures)
*   **US-AM-001:** 作为 Agent，我希望能够查询当前合约账户的余额信息（特别是保证金余额、可用余额），以便评估账户资金状况。
*   **US-AM-002:** 作为 Agent，我希望能够查询当前所有合约持仓的详细信息（如交易对、方向、数量、开仓均价、未实现盈亏、保证金、杠杆），以便管理现有头寸。
*   **US-AM-003:** 作为 Agent，我希望能够查询指定交易对当前的杠杆倍数和保证金模式（逐仓/全仓）。
*   **US-AM-004:** 作为 Agent，我希望能够为指定交易对设置杠杆倍数。
*   **US-AM-005:** 作为 Agent，我希望能够为指定逐仓模式下的持仓调整保证金。

### 2.4 Error Handling & Rate Limiting
*   **US-EH-001:** 作为 Agent，当调用交易所 API 发生错误时，我希望模块能够统一解析错误码和错误信息，并根据错误类型决定是重试操作还是向我报告错误。
*   **US-RL-001:** 作为 Agent，我希望模块能够内部管理并遵守交易所的 API 调用频率限制，避免因超限导致 API Key 被封禁。

## 3. Acceptance Criteria

### For US-MD-001 (Get Klines):
*   **Given** 我请求 BTCUSDT 的 1小时 K线数据，限制100条
*   **When** 模块调用 Binance API
*   **Then** 我能收到包含100条 BTCUSDT 1小时 K线数据的列表，每条数据包含时间、开盘价、最高价、最低价、收盘价和成交量。

### For US-OE-001 (Create Market Order):
*   **Given** 我的账户有足够余额，且 BTCUSDT 交易对可交易
*   **When** 我请求以市价买入 0.01 BTCUSDT 合约
*   **Then** 订单成功提交到 Binance，并返回订单 ID，后续我能查询到该订单的成交状态。

### For US-AM-001 (Get Account Balance):
*   **Given** 我的 API Key 有查询权限
*   **When** 我请求查询合约账户余额
*   **Then** 我能收到包含总保证金余额、可用保证金余额等关键信息的账户数据。

*(More ACs to be defined for other key stories)*

## 4. Scope

### 4.1. In Scope (MVP for market_interface_crypto):
*   集成 Binance USDⓈ-M Futures (合约) API。
*   实现上述用户故事中定义的核心功能：获取K线、Ticker、订单簿；创建市价/限价单、取消订单、查询订单；查询账户余额、持仓、杠杆/保证金模式；设置杠杆、调整保证金；统一错误处理和速率限制管理。
*   提供清晰的 Python 内部接口供 Agent 核心调用。
*   必要的单元测试和集成测试。

### 4.2. Out of Scope (MVP for market_interface_crypto):
*   Binance 现货 (Spot) 交易 API 的集成 (可作为后续迭代)。
*   Binance 其他类型合约 (如 COIN-M Futures) 的集成。
*   OKX, Bybit 或其他交易所的 API 集成 (可作为后续迭代)。
*   实时 WebSocket 行情数据流的直接处理 (MVP 阶段可能通过轮询获取 Ticker/订单簿，或 Agent 核心通过其他方式获取实时数据流并调用此模块的分析工具)。如果 `draft_technical_specs.md` 中提到的 WebSocket 服务由主后端提供，本模块可能仅消费其处理后的数据，或按需提供接口。
*   复杂的订单类型如 TWAP, VWAP 等。
*   资金划转功能。

## 5. Technical Notes / Assumptions
*   **Primary Exchange for MVP:** Binance (USDⓈ-M Futures).
*   **Binance API Version:** 将使用 Binance API 的最新稳定版本。
*   **Python Library:** 优先考虑使用官方或社区广泛认可的 Python Binance连接库，如 `python-binance`。需评估其对合约 API 的支持程度和稳定性。
*   **API Key Management:** API Key 的安全存储和管理由用户账户服务负责，本模块仅接收配置好的 Key 进行操作。
*   **Error Codes:** 需要整理和映射 Binance 合约 API 的常见错误码。
*   **Rate Limits:** 需要仔细阅读并遵守 Binance API 的速率限制文档。
*   **Data Structures:** 定义统一的内部数据结构来表示K线、订单、持仓等，以便未来扩展到其他交易所时保持接口一致性。
*   **Authentication:** 使用 API Key 和 Secret Key 进行签名认证。
*   **Testing:** 需要一个 Binance 合约测试网 (Testnet) 账户进行开发和测试。