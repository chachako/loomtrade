# Toolset & System Prompt Design Part A: Toolset Overview & Market Data Tools

This document begins the detailed specification of the Core Toolset (in English) available to all AI Agents. All tool calls **MUST** adhere to the specified XML format.

## I. Core Toolset (English) - Overview

This toolset is designed to be comprehensive yet atomic, allowing the LLM to combine tools to achieve complex tasks. The backend `ToolExecutor` will parse these XML blocks.

### General Tool Response Format
All tools, upon execution, should return a result to the LLM in a structured XML format, indicating success or failure.

*Success Example:*
```xml
<tool_result tool_name="[tool_name_here]">
    <status>success</status>
    <data>
        <!-- Tool-specific data payload -->
    </data>
</tool_result>
```

*Error Example:*
```xml
<tool_result tool_name="[tool_name_here]">
    <status>error</status>
    <error_details>
        <error_code>[internal_or_exchange_error_code]</error_code>
        <message>[Readable error message]</message>
        <details_json>[Optional JSON string with more details]</details_json>
    </error_details>
</tool_result>
```

---

### 1. Market Data Tools

*   **1.1 `get_historical_klines`**
    *   **Description:** Fetches historical K-line (candlestick) data for a specified trading symbol.
    *   **Invocation Format:**
        ```xml
        <get_historical_klines>
            <symbol>string</symbol> <!-- e.g., "BTC/USDT", "ETH/USDT" -->
            <interval>string</interval> <!-- e.g., "1m", "5m", "15m", "1h", "4h", "1d" -->
            <limit>integer</limit> <!-- Optional, e.g., 200. Default: 100. Max: 1000 (system defined) -->
            <end_time_ms>long</end_time_ms> <!-- Optional, Unix timestamp in milliseconds. Fetches klines before this time. -->
        </get_historical_klines>
        ```
    *   **Parameters:**
        *   `symbol` (string, required): The trading symbol.
        *   `interval` (string, required): The K-line interval.
        *   `limit` (integer, optional): Number of K-lines to fetch.
        *   `end_time_ms` (long, optional): Timestamp to fetch K-lines before.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <klines_data>
            <kline timestamp_ms="long" open="decimal" high="decimal" low="decimal" close="decimal" volume="decimal" />
            <!-- ... more klines ... -->
        </klines_data>
        ```

*   **1.2 `get_current_ticker_info`**
    *   **Description:** Fetches the latest price ticker information for one or more symbols.
    *   **Invocation Format:**
        ```xml
        <get_current_ticker_info>
            <symbols> <!-- At least one symbol required -->
                <symbol>string</symbol> <!-- e.g., "BTC/USDT" -->
                <symbol>string</symbol> <!-- e.g., "ETH/USDT" (optional, for multiple) -->
            </symbols>
        </get_current_ticker_info>
        ```
    *   **Parameters:**
        *   `symbols` (list of strings, required): Trading symbol(s).
    *   **Expected Output (Success Data Payload):**
        ```xml
        <tickers_data>
            <ticker symbol="string" last_price="decimal" high_24h="decimal" low_24h="decimal" volume_24h="decimal" change_percent_24h="decimal" />
            <!-- ... more tickers if multiple symbols requested ... -->
        </tickers_data>
        ```

*   **1.3 `get_order_book`**
    *   **Description:** Fetches the current order book (depth of market) for a symbol.
    *   **Invocation Format:**
        ```xml
        <get_order_book>
            <symbol>string</symbol>
            <limit>integer</limit> <!-- Optional, e.g., 20. Default: 10. Max: 100 (system defined) -->
        </get_order_book>
        ```
    *   **Parameters:**
        *   `symbol` (string, required): The trading symbol.
        *   `limit` (integer, optional): Number of bids/asks levels to return.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <order_book_data symbol="string">
            <bids>
                <level price="decimal" quantity="decimal" />
                <!-- ... more bid levels ... -->
            </bids>
            <asks>
                <level price="decimal" quantity="decimal" />
                <!-- ... more ask levels ... -->
            </asks>
        </order_book_data>