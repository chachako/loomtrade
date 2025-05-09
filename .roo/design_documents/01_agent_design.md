# Agent Design

This document details the design of the different types of AI Agents within the system, their responsibilities, memory structures, interaction patterns, and permission management. All agent LLMs will use a common, English-based System Prompt template and toolset (detailed in `03_toolset_and_system_prompt.md`), augmented with role-specific instructions. Agent runtime memory (YAML/Markdown files) will be stored in a configurable backend cache directory.

## 1. System Orchestrator Agent (SOA)

*   **1.1 Role & Core Responsibilities:**
    *   **Primary User Interface:** Acts as the main conversational entry point for users to interact with the trading agent system via natural language.
    *   **Natural Language Understanding (NLU) & Intent Recognition:** Utilizes its LLM to parse and understand user commands, queries, complex strategy descriptions, or requests to manage agents and tasks. It identifies the user's intent (e.g., query data, define a new automated strategy, control an existing agent, set up a monitoring alert).
    *   **Task Planning & Dispatching:** Based on the recognized intent, the SOA's LLM plans the necessary steps and uses internal tools to:
        *   **Execute Simple Requests:** Directly use tools (via `ToolExecutor`) for straightforward data queries (e.g., "What's Bitcoin's current price?") or simple actions, then relay results to the user.
        *   **Manage Specialized Agents:** Interact with the `AgentManager` tool to dynamically create, configure, start, stop, or modify specialized Analyst and Trader agent instances based on user's natural language strategy definitions (e.g., "Create an agent that buys BTC if 1h RSI is below 30 and MACD is positive...").
        *   **Control Existing Agents:** Process user commands like "Pause my ETH scalping agent" by instructing the `AgentManager`.
        *   **Schedule Background Tasks:** Interface with the `TaskScheduler` tool to set up recurring monitoring tasks as requested by the user (e.g., "Scan for high-volume altcoins every hour and alert me if X").
    *   **Dialog Management:** Maintains the conversational context with the user, enabling coherent multi-turn interactions.
    *   **Clarification & Feedback:** Proactively asks for clarification if user instructions are ambiguous (using `ask_user_clarification` tool) and provides feedback on its understanding or the status of requested actions.
    *   **Agentic Loop Adherence:** Operates on a standard think -> tool_call -> process_result -> think cycle.

*   **1.2 LLM Prompt Augmentation (Conceptual - added to General System Prompt):**
    *   *"Your specific role in this interaction is **System Orchestrator**. You are the primary interface for the user. Your key responsibilities include: Interpreting broad user commands related to strategy definition, agent creation, and system-level tasks. You will utilize tools like `create_new_agent_instance` to set up specialized Analyst or Trader agents, `dispatch_task_to_agent` to delegate specific analytical or trading tasks to existing agents, `schedule_background_job` for setting up monitoring routines, and `send_notification` to inform the user. You must guide the user through complex configurations if needed, using `ask_user_clarification`."*

*   **1.3 Memory (in Backend Cache Directory, e.g., `{cache_dir}/agent_memory/system_orchestrator/`):**
    *   `interaction_logs.md`: Records key user interactions, SOA's understanding, and dispatched actions.
    *   `user_preferences.yaml`: (Optional) Stores learned user preferences or common request patterns to personalize interactions over time.

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
        ```

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
        ```

## 4. Agent-to-Agent Communication / Workflow

*   **Primary Mechanism:** Asynchronous task/message dispatching via the `SystemOrchestratorAgent` or `AgentManager` (which would use an internal message queue or similar mechanism).
    *   Example: Analyst Agent generates a signal -> calls `dispatch_task_to_agent` tool -> `AgentManager` routes this signal (as a task payload) to the appropriate Trader Agent.
*   **Shared Context (Limited):** While direct messaging is primary, some high-level, slowly changing context (e.g., overall market sentiment if an agent is dedicated to it) could be written to a shared section of the Agent Memory (e.g., a specific file in a common area of the cache, or SOA distributes it), which other agents can read. This should be used sparingly to avoid tight coupling.
*   **SOA as Central Hub:** For user-initiated actions or complex multi-agent coordination, the SOA often acts as the central point, receiving user input and then dispatching specific sub-tasks to relevant Analyst or Trader agents.

## 5. Agent Permissions Management

*   **Storage:** Permissions will be stored as part of an agent's configuration, likely within its main config file in its memory directory (e.g., `agent_config.yaml`), managed by `AgentManager` and potentially set/modified by the SOA based on user instructions.
*   **Enforcement:** The `ToolExecutor` module will be the primary point of enforcement for critical actions. Before executing a sensitive tool call (especially `create_order`, `cancel_order`, `set_position_tp_sl`), it will:
    1.  Identify the calling `agent_instance_id`.
    2.  Load that agent's permissions from its configuration.
    3.  Verify if the requested action and its parameters (e.g., symbol, quantity, order type) are within the allowed limits.
*   **Permission Granularity (Examples):**
    *   `can_trade_symbols`: ["BTCUSDT", "ETHUSDT"] or "ALL_FUTURES" or `null` (no trading).
    *   `max_position_size_per_symbol_usd`: 5000
    *   `max_total_open_positions_usd`: 20000
    *   `max_order_quantity_per_trade_for_btc`: 0.5
    *   `allowed_order_types`: ["MARKET", "LIMIT"]
    *   `can_schedule_background_jobs`: true/false (for Analyst or SOA)
    *   `can_send_notifications_telegram`: true/false
*   **Default Profiles:** System can have predefined permission profiles (e.g., "ReadOnlyAnalyst", "CautiousTrader", "AggressiveTrader_SmallCap") that SOA can use when creating new agents.