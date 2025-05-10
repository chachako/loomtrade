# Decision Log: 币安合约市场接口 (Binance Futures Connector) (ID: F005_binance_connector)
*Initialized by Feature-Lead on 2025-05-10 11:33:34*
*Entries are prepended, newest first. Format: DECISION-F005_binance_connector-XXX: [YYYY-MM-DD HH:MM:SS] - Title*
---
DECISION-F005_binance_connector-003: [2025-05-10 11:37:13] - Python 库选择
    - 内容: 优先考虑直接使用 `requests` 库并自行实现签名和 API 调用逻辑，以获得最大控制权和最小化外部依赖。如果开发过程中发现过于复杂，可以重新评估使用 `python-binance` 等现有库的可行性，但需注意其维护状态和对特定 API 功能的支持程度。
---
DECISION-F005_binance_connector-002: [2025-05-10 11:37:13] - 认证机制
    - 内容: API 请求将使用 HMAC SHA256 进行签名认证，具体实现细节需严格遵循币安官方文档。
---
DECISION-F005_binance_connector-001: [2025-05-10 11:37:13] - 明确 API 端点和范围
    - 内容: 本连接器将专注于币安 USDT 本位永续合约，并使用官方 API V1 (`https://fapi.binance.com`)。API 密钥安全性和频率限制遵守是首要任务。错误处理将区分可重试和不可重试错误。WebSocket 实时数据流不在初始范围内。
---
<!-- No feature-specific decisions logged yet. -->