# Agent Design Part B: Analyst Agents (AA)

This document details the design of Analyst Agents (AA). Refer to `01a_agent_overview_and_soa.md` for the general agent overview.

## 2. Analyst Agents (AA)

*   **2.1 Core Responsibilities:**
    *   **Market Analysis:** Perform in-depth analysis of specified markets (MVP: Binance Contracts) and symbols based on assigned strategies and tasks (delegated by SOA or scheduled).
    *   **Signal Generation:** Identify potential trading opportunities or significant market events (e.g., trend changes, breakout confirmations) that meet the criteria of their active strategy.
    *   **LLM-Driven Insight (Key):** Go beyond simple indicator triggers. The Analyst Agent's LLM is prompted to:
        *   Interpret combinations of technical indicators (e.g., EMA, MACD, RSI, BBands, ADX, ATR, Volume).
        *   Analyze K-line patterns and price action in the context of indicators.
        *   Assess the quality, strength, and confidence level of potential signals.
        *   Consider market structure (e.g., ranging, trending, support/resistance).
        *   (Future) Incorporate other data sources like summarized news sentiment if tools become available.
    *   **Trend & Condition Monitoring:** Continuously monitor if the conditions underpinning an active signal or market assessment remain valid.
    *   **Specialization:** While a generic Analyst Agent template will exist, instances can be configured (or dynamically prompted by SOA) to specialize in certain strategies (e.g., LTECS, LARIMERS as designed previously) or market conditions.

*   **2.2 LLM Prompt Augmentation (Conceptual - for an LTECS Analyst):**
    *   *"Your specific role is **Market Analyst Agent for the LTECS (LLM-Enhanced Trend Evolution & Confirmation Strategy) focusing on {symbol} ({timeframe})**. You must:
        1. Fetch relevant K-line data and calculate EMA, MACD, ADX, ATR.
        2. Analyze these indicators to identify potential trend initiations or continuations.
        3. Evaluate the quality and confirmation level of these trend signals, considering price action, volume, and K-line patterns.
        4. Assess trend strength and potential for exhaustion.
        5. Generate a structured analysis report including trend direction, strength, confirmation level, key observations, and a suggested action bias.
        6. Log your detailed reasoning and findings in your `analysis_log.md`.
        7. If a high-confidence trading signal is identified, prepare a structured signal payload and dispatch it to the designated Trader Agent via the `dispatch_task_to_agent` tool."*

*   **2.3 Memory (in Backend Cache Directory, e.g., `{cache_dir}/agent_memory/{analyst_agent_id}/`):**
    *   `strategy_config.yaml`: Stores the specific strategy parameters, target symbols, and timeframes this instance is working with.
    *   `analysis_log.md`: Timestamped log of each analysis cycle: input data summary, LLM's detailed reasoning (if captured), indicator values, K-line observations, and the structured assessment/signal generated.
        ```markdown
        ---
        timestamp: 2025-05-10T14:30:00Z
        symbol: BTC/USDT
        timeframe: 1h
        strategy: LTECS_v1
        llm_input_summary: "Klines (last 200), EMA(12/26), MACD(12/26/9), ADX(14), ATR(14)"
        llm_assessment:
          trend_direction: "bullish"
          trend_strength: "developing"
          confirmation_level: "medium"
          key_observations_text: "EMA12 crossed above EMA26 with increasing volume. MACD histogram turned positive. ADX rising above 22. Price broke minor resistance at 65200."
          suggested_action_bias: "cautious_long_bias"
          potential_entry_trigger_condition_summary: "Entry on pullback to EMA12 or break of 65500."
          initial_risk_parameters_suggestion: { atr_value: 150, suggested_sl_atr_multiple: 1.5 }
        signal_dispatched_to_trader_id: "trader_agent_xyz" # If signal was strong enough
        ---
        ```
    *   `market_context_beliefs.yaml`: The agent's evolving understanding of the market(s) it monitors.
        ```yaml
        BTC/USDT:
          last_analysis_1h: 2025-05-10T14:30:00Z
          current_trend_1h: "developing_bullish"
          estimated_support_1h: 64800
          estimated_resistance_1h: 66000
          active_trend_signal_id: "ltecs_btc_long_signal_001"
        ETH/USDT:
          # ... similar structure