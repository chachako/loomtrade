# Toolset & System Prompt Design Part B: Indicator & Order Tools

This document continues the detailed specification of the Core Toolset. Refer to `03a_toolset_overview_and_market_data.md` for the general toolset overview and response format.

---

### 2. Technical Indicator Tools

*   **2.1 `calculate_technical_indicator`**
    *   **Description:** Calculates a specified technical indicator based on provided K-line data.
    *   **Invocation Format:**
        ```xml
        <calculate_technical_indicator>
            <indicator_name>string</indicator_name> <!-- e.g., "RSI", "EMA", "MACD", "BBANDS", "ATR", "STOCH" -->
            <klines_json>string_json_array</klines_json> <!-- JSON string of klines array: [{"timestamp_ms":long,"open":dec,"high":dec,"low":dec,"close":dec,"volume":dec}, ...] -->
            <parameters_json>string_json_object</parameters_json> <!-- JSON string of indicator-specific parameters, e.g., {"period": 14} for RSI -->
        </calculate_technical_indicator>
        ```
    *   **Parameters:**
        *   `indicator_name` (string, required): Name of the indicator (e.g., "RSI", "EMA", "MACD", "BBANDS", "ATR", "STOCH").
        *   `klines_json` (string, required): JSON string representation of an array of K-line objects (typically obtained from `get_historical_klines` tool and then stringified by the LLM). The structure should be consistent: `[{"timestamp_ms": long, "open": decimal, "high": decimal, "low": decimal, "close": decimal, "volume": decimal}, ...]`.
        *   `parameters_json` (string, required): JSON string of an object containing parameters specific to the indicator. Examples:
            *   For RSI: `{"period": 14}`
            *   For EMA: `{"period": 20}`
            *   For MACD: `{"fast_period": 12, "slow_period": 26, "signal_period": 9}`
            *   For BBANDS: `{"period": 20, "std_dev": 2}`
            *   For ATR: `{"period": 14}`
            *   For STOCH: `{"k_period": 14, "d_period": 3, "smooth_k": 3}`
    *   **Expected Output (Success Data Payload - example for RSI):**
        ```xml
        <indicator_result indicator_name="RSI">
            <values_json>string_json_array</values_json> <!-- JSON string of an array of numbers, e.g., "[null, ..., 30.5, 32.1]" (initial values might be null due to period) -->
        </indicator_result>
        ```
        *Note: For complex indicators like MACD, `values_json` would be a JSON string of an object containing multiple arrays: `{"macd_line":[...], "signal_line":[...], "histogram":[...]}`. For BBANDS: `{"upper_band":[...], "middle_band":[...], "lower_band":[...]}`.*

---

### 3. Account & Order Management Tools (Binance Contracts Specific for MVP)

*   **3.1 `get_account_balance`**
    *   **Description:** Fetches current account balance information for the configured Binance Futures account.
    *   **Invocation Format:**
        ```xml
        <get_account_balance />
        ```
    *   **Parameters:** None for MVP (assumes a single, pre-configured Binance account via API keys).
    *   **Expected Output (Success Data Payload):**
        ```xml
        <account_balance_data>
            <asset name="USDT" wallet_balance="decimal" available_balance="decimal" unrealized_pnl="decimal" />
            <!-- Other relevant margin assets might be listed if applicable -->
            <total_margin_balance_usd="decimal" />
            <total_wallet_balance_usd="decimal" />
            <total_available_balance_usd="decimal" />
            <total_unrealized_pnl_usd="decimal" />
        </account_balance_data>
        ```

*   **3.2 `get_open_positions`**
    *   **Description:** Fetches all currently open positions in the Binance Futures account.
    *   **Invocation Format:**
        ```xml
        <get_open_positions>
            <symbol>string</symbol> <!-- Optional. If provided, fetches position for a specific symbol (e.g., "BTCUSDT"). -->
        </get_open_positions>
        ```
    *   **Parameters:**
        *   `symbol` (string, optional): Specific symbol to query. If omitted, all open positions are returned.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <positions_data>
            <position symbol="string" side="LONG|SHORT" quantity="decimal" entry_price="decimal" mark_price="decimal" unrealized_pnl="decimal" liquidation_price="decimal" leverage="integer" initial_margin="decimal" isolated_wallet="decimal" position_value_usd="decimal"/>
            <!-- ... more positions ... -->
        </positions_data>
        ```

*   **3.3 `create_order`**
    *   **Description:** Places a new order on Binance Futures.
    *   **Invocation Format:**
        ```xml
        <create_order>
            <symbol>string</symbol> <!-- e.g., "BTCUSDT" (Binance Futures symbols typically don't use '/') -->
            <side>string</side> <!-- "BUY" (for Long) or "SELL" (for Short) -->
            <type>string</type> <!-- "MARKET", "LIMIT", "STOP_MARKET", "TAKE_PROFIT_MARKET", "TRAILING_STOP_MARKET" -->
            <quantity>decimal</quantity> <!-- Order quantity in base asset (e.g., number of BTC for BTCUSDT) -->
            <price>decimal</price> <!-- Optional: Required for LIMIT orders. For TAKE_PROFIT_MARKET and STOP_MARKET, this is the trigger price. -->
            <stop_price>decimal</stop_price> <!-- Optional: Used for STOP_MARKET, TAKE_PROFIT_MARKET (trigger price), and TRAILING_STOP_MARKET (activation price). -->
            <callback_rate>decimal</callback_rate> <!-- Optional: Used for TRAILING_STOP_MARKET (e.g., 1 for 1% callback rate). -->
            <reduce_only>boolean</reduce_only> <!-- Optional: "true" or "false". Default: "false". Ensure position can only be reduced. -->
            <time_in_force>string</time_in_force> <!-- Optional: For LIMIT orders, e.g., "GTC" (Good-Til-Canceled), "IOC" (Immediate-Or-Cancel), "FOK" (Fill-Or-Kill). Default: "GTC". -->
            <new_client_order_id>string</new_client_order_id> <!-- Optional: A unique ID for the order generated by the client. -->
        </create_order>
        ```
    *   **Parameters:** As listed in the XML structure. Ensure `symbol` format matches exchange requirements.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <order_created_data
            exchange_order_id="string"
            client_order_id="string"
            symbol="string"
            side="string"
            type="string"
            quantity_ordered="decimal"
            status="string" <!-- e.g., "NEW", "PARTIALLY_FILLED", "FILLED" (MARKET orders usually return FILLED quickly) -->
            price_ordered="decimal" <!-- For LIMIT orders -->
            average_fill_price="decimal" <!-- If (partially) filled -->
            cumulative_filled_quantity="decimal" <!-- If (partially) filled -->
        />
        ```

*   **3.4 `cancel_order`**
    *   **Description:** Cancels an open (unfilled or partially filled) order.
    *   **Invocation Format:**
        ```xml
        <cancel_order>
            <symbol>string</symbol> <!-- e.g., "BTCUSDT" -->
            <exchange_order_id>string</exchange_order_id> <!-- The order ID assigned by Binance -->
            <!-- OR <client_order_id>string</client_order_id> --> <!-- Alternatively, use the client-generated ID if provided during creation -->
        </cancel_order>
        ```
    *   **Parameters:**
        *   `symbol` (string, required).
        *   `exchange_order_id` (string, one of this or `client_order_id` is required).
        *   `client_order_id` (string, one of this or `exchange_order_id` is required).
    *   **Expected Output (Success Data Payload):**
        ```xml
        <order_cancelled_data
            exchange_order_id="string"
            client_order_id="string"
            symbol="string"
            status="string" <!-- e.g., "CANCELED" -->
        />
        ```

*   **3.5 `set_position_tp_sl_orders`**
    *   **Description:** A utility tool to place associated Take Profit (TP) and/or Stop Loss (SL) orders for an existing position. These are typically `TAKE_PROFIT_MARKET` and `STOP_MARKET` orders with `reduce_only=true`.
    *   **Invocation Format:**
        ```xml
        <set_position_tp_sl_orders>
            <symbol>string</symbol> <!-- e.g., "BTCUSDT" -->
            <position_side>string</position_side> <!-- "LONG" or "SHORT" (This is the side of the *existing position* you want to protect) -->
            <position_quantity>decimal</position_quantity> <!-- The quantity of the existing position to be covered by these TP/SL orders. -->
            <take_profit_price>decimal</take_profit_price> <!-- Optional. The trigger price for the Take Profit order. -->
            <stop_loss_price>decimal</stop_loss_price> <!-- Optional. The trigger price for the Stop Loss order. -->
        </set_position_tp_sl_orders>
        ```
    *   **Parameters:**
        *   `symbol` (string, required).
        *   `position_side` (string, required): The side of the current open position. If "LONG", TP will be a SELL, SL will be a SELL. If "SHORT", TP will be a BUY, SL will be a BUY.
        *   `position_quantity` (decimal, required): The amount of the position these TP/SL orders should close.
        *   `take_profit_price` (decimal, optional): If provided, a TAKE_PROFIT_MARKET order will be placed.
        *   `stop_loss_price` (decimal, optional): If provided, a STOP_MARKET order will be placed.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <tp_sl_orders_set_result symbol="string">
            <take_profit_order_details> <!-- Present only if take_profit_price was provided -->
                <order_created_data exchange_order_id="string" client_order_id="string" status="string" type="TAKE_PROFIT_MARKET" side="BUY|SELL" price_ordered="decimal" quantity_ordered="decimal"/>
            </take_profit_order_details>
            <stop_loss_order_details> <!-- Present only if stop_loss_price was provided -->
                <order_created_data exchange_order_id="string" client_order_id="string" status="string" type="STOP_MARKET" side="BUY|SELL" price_ordered="decimal" quantity_ordered="decimal"/>
            </stop_loss_order_details>
            <message>string</message> <!-- e.g., "Take profit and stop loss orders successfully placed." or "Only take profit order placed." -->
        </tp_sl_orders_set_result>
        ```
        *Self-correction: The `side` in the output `order_created_data` for TP/SL orders will be opposite to the `position_side`.*