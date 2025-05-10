# Agent Design Part C: Trader Agents (TA)

This document details the design of Trader Agents (TA). Refer to `01a_agent_overview_and_soa.md` for the general agent overview.

## 3. Trader Agents (TA)

*   **3.1 Core Responsibilities:**
    *   **Final Decision Authority:** Receives structured trading signals (including analysis context, suggested risk parameters) from one or more Analyst Agents.
    *   **Experience-Based Validation (Key):** Before acting on any signal, the Trader Agent **MUST** consult its own historical performance data and learned lessons for the **specific trading symbol** mentioned in the signal. This is done by its LLM querying its own memory files.
    *   **Trade Execution:** If the LLM, after considering both the analyst's signal and its own historical experience with that symbol/setup, decides to proceed, it then uses tools to:
        *   Calculate precise position size based on account balance and risk parameters (from strategy or user config).
        *   Place orders (`create_order`).
        *   Set initial stop-loss and take-profit orders (`set_position_tp_sl` or via `create_order`).
    *   **Position Management:** Monitor open positions, potentially adjusting TP/SL based on evolving market conditions (if strategy dictates and LLM agrees) or signals from Analyst Agents (e.g., "trend exhausting").
    *   **Record Keeping:** Meticulously log every trade decision, order placement, execution detail, and a post-trade reflection (LLM-generated) into its symbol-specific memory files.

*   **3.2 LLM Prompt Augmentation (Conceptual):**
    *   *"Your specific role is **Trader Agent**. You have received the following trading signal for {symbol} from an Analyst Agent: {analyst_signal_payload_json}.
        1. Query your memory files (`trades.yaml`, `performance_summary.yaml`) for {symbol} to retrieve your past performance and lessons learned with similar signals or market conditions for this specific symbol.
        2. Based on the Analyst's signal AND your historical experience with {symbol}, decide if this trade should be taken. Clearly state your reasoning.
        3. If you decide to trade:
            a. Calculate the appropriate position size based on current account balance {current_balance_details_json} and the risk parameters defined in the signal or your general configuration.
            b. Formulate the `create_order` tool call.
            c. Formulate subsequent `set_position_tp_sl` tool calls if applicable.
        4. If you decide NOT to trade, clearly state why, referencing your historical data for {symbol} if relevant.
        5. Log your decision, reasoning, and any actions taken (or not taken) in your trade log for {symbol}."*

*   **3.3 Memory (in Backend Cache Directory, e.g., `{cache_dir}/agent_memory/{trader_agent_id}/trade_history/{SYMBOL_standardized}/`):**
    *   `trades.yaml`: Detailed log of each executed trade for that symbol.
        ```yaml
        # Example for .../trader_001/trade_history/BTCUSDT/trades.yaml
        - trade_id: "TA001_BTC_20250510_001"
          symbol: "BTCUSDT"
          entry_timestamp: "2025-05-10T15:00:00Z"
          exit_timestamp: "2025-05-10T18:30:00Z"
          side: "LONG"
          quantity: 0.05
          entry_price: 65300.00
          exit_price: 65900.00
          pnl_usd: 28.50 # Net PnL
          fees_usd: 1.50
          analyst_signal_ref: "AA_LTECS_XYZ_signal_056"
          llm_decision_rationale_entry: |
            Analyst signal (LTECS_v1, 1h BTC/USDT, bullish confirmation medium) received.
            My history for BTCUSDT with LTECS-like entries in 'developing_bullish' 1h trend: 12 trades, 67% win rate, avg RRR 1.8.
            Current volatility is moderate. Risking 1% of available balance. Calculated position size 0.05 BTC. SL at 64800 (1.5x ATR from signal). TP at 66800 (3R). Proceeding.
          llm_decision_rationale_exit: |
            TP hit. Price action was smooth.
          lessons_learned_this_trade: "3R target was achievable in this trend leg. Good entry confirmation from analyst."
        ```
    *   `open_orders.yaml`: Tracks currently open orders for that symbol.
    *   `performance_summary.yaml`: Statistics for that symbol (win rate, avg PnL, etc.), periodically updated.
        ```yaml
        # Example for .../trader_001/trade_history/BTCUSDT/performance_summary.yaml
        symbol: "BTCUSDT"
        total_trades_taken: 13
        win_rate: 0.615 # Approx 61.5%
        # ... other stats as previously designed ...
        llm_strategy_effectiveness_notes_for_symbol: |
          The LTECS strategy on BTCUSDT 1h has shown positive expectancy.
          Mean reversion (LARIMERS) signals on BTCUSDT 15m require very careful filtering of range quality; historical performance mixed.
          Avoid taking LTECS signals if ADX is below 20, as per past losing trades.
        last_updated: "2025-05-10T19:00:00Z"