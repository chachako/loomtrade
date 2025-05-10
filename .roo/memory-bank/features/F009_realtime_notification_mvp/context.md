# Feature Context: 实时通信与通知服务 MVP (ID: F009_realtime_notification_mvp)
*Initialized by Feature-Lead on 2025-05-10 12:42:36*
*Last refined by Feature-Lead on 2025-05-10 12:43:41*

## 1. Overview & Goal
本功能的核心目标是实现一个 MVP (最小可行产品) 版本的实时通信与通知服务。
这主要包括两个组件：
1.  **WebSocketServer**: 建立一个 WebSocket 服务器，允许前端客户端 (F001) 建立持久连接，以接收来自后端的实时更新和通知。
2.  **NotificationService**: 一个后端服务，负责收集来自系统其他部分（如 Trader Agents F007, Analyst Agents F006）的重要事件和通知，并通过 WebSocketServer 将这些信息推送给已连接的前端客户端。
MVP 阶段的通知类型可能包括：新的交易信号、订单状态更新（成交、失败）、关键系统警报等。
目标是为用户提供关键事件的即时反馈，增强系统的交互性和透明度。

## 2. Detailed Requirements / User Stories
*   作为一名用户，我希望能够实时接收到新的交易信号通知，以便我能及时做出交易决策。
*   作为一名用户，我希望能够实时接收到我的订单状态更新（如已成交、部分成交、已取消、失败），以便我能了解我的交易执行情况。
*   作为一名用户，我希望能够实时接收到关键的系统警报（如连接中断、服务异常），以便我能了解系统当前状态。
*   作为一名系统管理员/开发者，我希望 WebSocket 连接是安全的，并且有明确的认证/授权机制，以防止未经授权的访问。

## 3. Acceptance Criteria
*   **AC1 (交易信号):** 当一个新的交易信号产生时，已连接的前端客户端能在 2 秒内收到包含信号详情的 WebSocket 消息。
*   **AC2 (订单状态):** 当一个订单状态发生变化时，相关的已连接前端客户端能在 2 秒内收到包含订单 ID 和新状态的 WebSocket 消息。
*   **AC3 (系统警报):** 当一个关键系统警报触发时，所有已连接的前端客户端能在 5 秒内收到警报信息。
*   **AC4 (安全连接):** WebSocket 连接必须使用 WSS (Secure WebSocket)。
*   **AC5 (认证):** 只有经过身份验证的用户才能成功建立 WebSocket 连接。

## 4. Scope
### 4.1. In Scope:
*   WebSocket 服务器的建立和基本连接管理 (连接、断开、心跳)。
*   基于 Token 的 WebSocket 连接身份验证 (具体机制待与 F001_frontend_core Feature Lead 协调)。
*   NotificationService 核心逻辑，用于收集和格式化通知。
*   NotificationService 推送三种核心通知类型到 WebSocketServer：新交易信号、订单状态更新、关键系统警报。
*   定义清晰的 WebSocket 消息格式 (JSON)。
*   基本的服务端错误处理和日志记录。
*   WebSocketServer 和客户端之间的心跳机制。

### 4.2. Out of Scope:
*   复杂的通知订阅/过滤机制 (MVP 阶段所有已连接客户端接收所有其有权访问的通知)。
*   历史通知的存储和检索。
*   通知内容的国际化/本地化。
*   WebSocket 服务器的横向扩展和负载均衡 (MVP 阶段关注单点可靠性)。
*   非常详细或大量的自定义通知类型 (超出 MVP 定义的三种)。
*   客户端重连逻辑的具体实现 (客户端责任，但服务器应支持重连)。

## 5. Technical Notes / Assumptions
### 5.1. WebSocket 消息格式:
所有 WebSocket 消息应为 JSON 格式。基本结构如下：
```json
{
  "type": "notification", // 可能的值: "notification", "error", "ack", "heartbeat"
  "event": "new_trade_signal", // 事件类型, e.g., "new_trade_signal", "order_update", "system_alert"
  "timestamp": "YYYY-MM-DDTHH:mm:ss.sssZ", // ISO 8601 格式的 UTC 时间戳
  "payload": {
    // 特定于 event 类型的内容
  }
}
```

### 5.2. 认证与授权 (Authentication & Authorization):
*   客户端在发起 WebSocket 连接请求时，应在 HTTP Header (e.g., `Sec-WebSocket-Protocol` 或自定义头) 或初始的 WebSocket 消息中传递一个有效的身份验证 Token (例如 JWT)。
*   WebSocketServer 将在连接握手阶段或收到第一个消息时验证此 Token。无效或缺失 Token 将导致连接被拒绝。
*   一旦连接建立，用户的身份应与该 WebSocket 会话关联，用于未来可能的权限控制。MVP 阶段主要关注连接级别的认证。

### 5.3. MVP 通知事件类型详情:
1.  **`new_trade_signal`**:
    ```json
    {
      "type": "notification",
      "event": "new_trade_signal",
      "timestamp": "...",
      "payload": {
        "signal_id": "string", // 唯一信号 ID
        "instrument_id": "string", // 例如 "BTC/USDT"
        "direction": "BUY" | "SELL",
        "entry_price": "number", // 建议入场价格
        "stop_loss": "number", // 止损价格
        "take_profit": ["number"], // 止盈价格 (可以有多个)
        "source_agent_id": "string", // 例如 "AnalystAgent-001"
        "confidence": "number" // (0.0 to 1.0) (可选)
      }
    }
    ```
2.  **`order_update`**:
    ```json
    {
      "type": "notification",
      "event": "order_update",
      "timestamp": "...",
      "payload": {
        "order_id": "string", // 平台订单 ID
        "client_order_id": "string", // (可选) 客户端自定义订单 ID
        "instrument_id": "string",
        "status": "SUBMITTED" | "PARTIALLY_FILLED" | "FILLED" | "CANCELED" | "REJECTED" | "EXPIRED",
        "side": "BUY" | "SELL",
        "type": "LIMIT" | "MARKET",
        "quantity_total": "number", // 总数量
        "quantity_filled": "number", // 已成交数量
        "price_avg_filled": "number", // (可选) 平均成交价格
        "reason_failed": "string" // (可选) 如果 REJECTED 或 EXPIRED，失败原因
      }
    }
    ```
3.  **`system_alert`**:
    ```json
    {
      "type": "notification",
      "event": "system_alert",
      "timestamp": "...",
      "payload": {
        "alert_id": "string", // 唯一警报 ID
        "level": "INFO" | "WARNING" | "ERROR" | "CRITICAL",
        "message": "string", // 警报内容
        "component": "string" // (可选) 产生警报的系统组件
      }
    }
    ```

### 5.4. 技术选型考虑:
*   **WebSocketServer:** 需考虑与现有后端技术栈 (Python 为主) 的兼容性和性能。可选项包括:
    *   Python: FastAPI-WebSocket, Django Channels, AIOHTTP WebSockets。
    *   备选: Node.js (e.g., `ws` library, `Socket.IO`) 如果有特定性能或生态需求，但需考虑跨语言集成。
*   **NotificationService:**
    *   可以作为独立的 Python 微服务。
    *   与其他服务 (Trader Agents F007, Analyst Agents F006) 的通信机制：
        *   优选: 异步消息队列 (e.g., Redis Streams, Kafka, RabbitMQ) 以实现解耦和削峰填谷。
        *   备选: 内部 gRPC 或 REST API 调用 (需考虑同步调用的潜在影响)。
*   **心跳机制 (Heartbeat):**
    *   服务器可以定期向客户端发送 `{"type": "heartbeat", "event": "ping", "timestamp": "..."}`。
    *   客户端应在收到 `ping` 后回复 `{"type": "heartbeat", "event": "pong", "timestamp": "..."}`。
    *   服务器若在一定时间内未收到 `pong` 或客户端消息，可认为连接丢失。客户端同理。
*   **错误处理消息:**
    ```json
    {
      "type": "error",
      "event": "auth_failed" | "invalid_message" | "internal_server_error",
      "timestamp": "...",
      "payload": {
        "message": "Descriptive error message",
        "code": "string" // (可选) 内部错误码
      }
    }
    ```

### 5.5. 可扩展性 (MVP 初级考虑):
*   WebSocketServer 应尽可能设计为无状态或易于水平扩展的连接处理逻辑。认证信息和用户会话数据可考虑存储在外部缓存 (如 Redis) 中，而非服务器内存。
*   NotificationService 通过消息队列接收事件本身有助于扩展性。

### 5.6. 与 F001_frontend_core 协调:
*   WebSocket 连接的认证 Token 格式和传递方式。
*   客户端如何处理心跳。
*   客户端如何解析和展示不同类型的通知。