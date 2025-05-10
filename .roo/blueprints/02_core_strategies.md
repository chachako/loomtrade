# Core Trading Strategies Design

This document outlines two core trading strategies designed for the AI Trading Agent system, with a focus on leveraging LLM capabilities for enhanced analysis and decision-making in the Binance cryptocurrency contracts market.

## Strategy 1: LLM-Enhanced Trend Evolution & Confirmation Strategy (LTECS)

*   **1.1 Strategy Rationale:**
    *   Traditional trend-following strategies (e.g., moving average crossovers, MACD signals) can be prone to false signals and whipsaws in the volatile crypto market.
    *   LTECS aims to improve upon this by using an LLM's analytical capabilities to provide deeper confirmation of potential trend signals.
    *   The LLM evaluates the quality of signals by considering market structure, K-line patterns, volume, and volatility, rather than just relying on indicator crossovers.
    *   It also attempts to understand the "evolutionary stage" and strength of a trend.

*   **1.2 Applicable Market & Timeframes:**
    *   **Market:** Binance Cryptocurrency Contracts (MVP focus).
    *   **Symbols:** Suitable for major, liquid contracts (e.g., BTC/USDT, ETH/USDT).
    *   **Timeframes:** Configurable by the user. Recommended to start with medium to longer-term charts (e.g., 1-hour, 4-hour) for more stable trends, but can be adapted for shorter timeframes (e.g., 15-minute) with increased risk awareness. Analyst Agents will perform analysis based on the configured primary timeframe.

*   **1.3 Core Indicators & Parameters (User/SOA Configurable):**
    *   **Exponential Moving Averages (EMA):** A shorter-period EMA (e.g., 12 or 20) and a longer-period EMA (e.g., 26 or 50).
    *   **Moving Average Convergence Divergence (MACD):** Standard parameters (e.g., 12, 26, 9) or adjustable.
    *   **Average Directional Index (ADX):** Period (e.g., 14) to measure trend strength.
    *   **Average True Range (ATR):** Period (e.g., 14) for dynamic stop-loss placement and potential take-profit targeting.
    *   **Volume:** (Optional, but highly recommended) Volume moving average to confirm breakout strength.

*   **1.4 LLM's Role in Analyst Agent (Prompting Concepts):**
    *   **Data Inputs for LLM:** Current and historical K-line data (OHLCV), calculated values for EMA, MACD, ADX, ATR. Optionally, key support/resistance levels (LLM-identified or user-defined).
    *   **Guiding LLM Analysis (Conceptual Prompt Snippets - to be refined in English for the actual System Prompt):**
        *   *"As an expert crypto market analyst for {pair} on the {timeframe} chart, assess the current trend using the provided K-line data and indicator values (EMA, MACD, ADX, ATR).
        *   **Trend Identification & Confirmation:**
            *   If an EMA crossover (e.g., EMA12 above EMA26 for bullish) is observed, evaluate its significance. Is it corroborated by MACD signals (e.g., MACD line above signal, positive/growing histogram)? Does ADX indicate a strengthening trend (e.g., rising and above 20-25)?
            *   Describe the price action accompanying the crossover: Was it a decisive break with strong momentum, or hesitant? Analyze volume during potential trend initiation – was it significantly above average?
            *   Are there confirming K-line patterns (e.g., large engulfing candle, Marubozu) supporting the new trend direction?
        *   **Trend Strength & Quality Assessment:**
            *   Based on ADX value and its slope, classify the current trend's strength (e.g., "weak," "developing," "strong," "maturing," "exhausting").
            *   Are there any bearish/bullish divergences (e.g., price making new highs but MACD/RSI failing to confirm) that might undermine conviction in the current trend?
        *   **Risk Assessment & Parameter Suggestion (Preliminary):**
            *   Given the current ATR, what's a logical initial stop-loss (e.g., 1.5x ATR, 2x ATR from entry or key level)?
            *   Is current volatility unusually high, suggesting a wider stop or reduced position size?
        *   **Structured Output Required:**
            *   `trend_direction`: "bullish", "bearish", "ranging/unclear"
            *   `trend_strength`: (as per your assessment)
            *   `confirmation_level`: "low", "medium", "high" (based on confluence)
            *   `key_observations_text`: (Your detailed reasoning, citing K-line/indicator evidence)
            *   `suggested_action_bias`: "strong_long", "cautious_long", "neutral", "cautious_short", "strong_short"
            *   `potential_entry_trigger_summary`: (e.g., "Enter on pullback to EMA20 if trend strong," or "Enter on break of recent high if ADX confirms")
            *   `initial_risk_params_suggestion`: { `atr_value`: X, `suggested_sl_atr_multiple`: Y }
        *   Log your detailed thought process and this structured assessment."*

*   **1.5 Entry Conditions (Signal from Analyst, Confirmed by Trader):**
    *   **Long:**
        1.  Short-period EMA crosses above long-period EMA.
        2.  MACD bullish crossover or MACD histogram positive and expanding.
        3.  ADX > 20 (or 25) and rising (or +DI > -DI).
        4.  **LLM Confirmation (from Analyst Agent):**
            *   `confirmation_level` is "medium" or "high."
            *   `key_observations_text` supports the bullish direction without significant contradictory evidence.
            *   (If analyzed) Volume supports breakouts.
        5.  (Optional, LLM-suggested or strategy config) Entry on a slight pullback to the shorter EMA or on a breakout of a recent swing high.
    *   **Short:** Converse conditions.

*   **1.6 Exit Conditions:**
    *   **Stop-Loss:**
        *   Initial SL: N x ATR below entry (long) or above entry (short) (e.g., N=1.5 or 2). LLM can suggest N based on volatility/trend strength.
        *   Trailing Stop: Can be implemented (e.g., trail by N x ATR or fixed percentage once in profit).
    *   **Take-Profit:**
        *   Risk-Reward Ratio (RRR): Target N times the initial risk (e.g., 2R, 3R).
        *   Trend Exhaustion Signals: ADX falling below a threshold, significant price-indicator divergence, counter-EMA crossover. LLM (Analyst) periodically re-assesses trend and can signal "trend exhausting" or "confirmation significantly weakened."
    *   **Time-Based Exit:** (Optional) If position is open for an extended period without progress and trend stagnates.

*   **1.7 Position Sizing (Preliminary):**
    *   Fixed fractional risk: Risk a set percentage of account equity per trade (e.g., 1-2%).
    *   Volatility-adjusted: Reduce size when ATR is high to maintain consistent USD risk.

*   **1.8 Implementation in Agent Framework:**
    *   **SOA:** User defines/selects LTECS, specifying symbol, timeframe, risk params. SOA instructs `AgentManager` to create/configure an AA_LTECS and a TA_Main.
    *   **Analyst Agent (AA_LTECS):**
        1.  Triggered periodically by `TaskScheduler` or SOA.
        2.  Uses tools: `get_historical_klines`, `calculate_technical_indicator`.
        3.  Submits data to its LLM with LTECS-specific prompt augmentations.
        4.  Receives structured assessment from LLM.
        5.  If entry conditions met with sufficient confidence, generates a structured signal (including analysis summary, risk suggestions) and dispatches it to TA_Main via `dispatch_task_to_agent`.
        6.  Logs all analysis to its memory (`analysis_log.md`, `market_context_beliefs.yaml`).
    *   **Trader Agent (TA_Main):**
        1.  Receives signal from AA_LTECS.
        2.  **Crucial Step:** Uses tools to read its own memory for that symbol (`trades.yaml`, `performance_summary.yaml`).
        3.  Its LLM evaluates the analyst's signal *in conjunction with its own historical performance data* for similar setups on that symbol.
        4.  If LLM confirms, calculates final position size.
        5.  Uses tools: `get_account_balance`, `create_order`, `set_position_tp_sl`.
        6.  Logs decision and trade details to its symbol-specific `trades.yaml`.
        7.  Monitors position, potentially acting on exit signals from AA_LTECS or its own pre-set TP/SL.

## Strategy 2: LLM-Assisted Range Identification & Mean Reversion Strategy (LARIMERS)

*   **2.1 Strategy Rationale:**
    *   Crypto markets often exhibit periods of consolidation or ranging behavior. LARIMERS aims to capitalize on these by trading mean reversion signals near the boundaries of an identified range.
    *   The LLM's primary role is to assist in robustly identifying whether the market is in a "tradeable range" (distinguishing it from trend continuations or erratic chop) and to confirm the quality of reversal signals at range extremes using indicators and K-line patterns.

*   **2.2 Applicable Market & Timeframes:**
    *   **Market:** Binance Cryptocurrency Contracts.
    *   **Symbols:** Best suited for symbols that historically show clear ranging behavior.
    *   **Timeframes:** Typically 15-minute to 1-hour charts for identifying and trading ranges.

*   **2.3 Core Indicators & Parameters:**
    *   **Bollinger Bands (BB):** Period (e.g., 20), Standard Deviations (e.g., 2).
    *   **Relative Strength Index (RSI):** Period (e.g., 14), Overbought (e.g., 70-80), Oversold (e.g., 20-30).
    *   **Stochastic Oscillator:** %K, %D, Smooth (e.g., 14, 3, 3), Overbought (e.g., 80), Oversold (e.g., 20).
    *   **K-line Patterns:** (LLM-assisted identification) e.g., Pin Bars, Engulfing patterns, Dojis at key levels.

*   **2.4 LLM's Role in Analyst Agent (Prompting Concepts):**
    *   **Data Inputs for LLM:** K-line data, calculated BB, RSI, Stochastic values.
    *   **Guiding LLM Analysis (Conceptual Prompt Snippets):**
        *   *"As an expert range trading analyst for {pair} on {timeframe}, assess if the market is in a tradeable range.
        *   **Range Identification & Validation:**
            *   Analyze Bollinger Bands: Is price largely contained? Are bands parallel/contracting?
            *   Describe price action at BB boundaries: Reversals or breakout attempts?
            *   Are horizontal support/resistance levels aligning with BBs?
            *   Conclude: "tradeable_range," "potential_breakout," "trending," or "choppy_unclear."
        *   **Signal Confirmation (if in "tradeable_range"):**
            *   At Upper BB/Resistance: RSI overbought? Stochastic overbought + bearish cross? Bearish K-line pattern?
            *   At Lower BB/Support: RSI oversold? Stochastic oversold + bullish cross? Bullish K-line pattern?
        *   **Structured Output Required:**
            *   `market_condition`: (as above)
            *   `range_boundaries_estimate`: { `upper`: X, `lower`: Y, `confidence`: "low/medium/high" }
            *   `current_signal_at_boundary`: "sell_at_upper", "buy_at_lower", "none"
            *   `signal_confirmation_level`: "low", "medium", "high" (confluence of indicators & K-lines)
            *   `key_observations_text`: (Detailed reasoning)
        *   Log your analysis."*

*   **2.5 Entry Conditions:**
    *   **Long:**
        1.  Analyst LLM: `market_condition: "tradeable_range"` with medium/high `range_boundaries_estimate.confidence`.
        2.  Price near Lower BB / identified range support.
        3.  RSI oversold + turning up.
        4.  Stochastic oversold + bullish crossover.
        5.  **LLM Confirmation:** `current_signal_at_boundary: "buy_at_lower"` with medium/high `signal_confirmation_level`, supported by bullish K-line patterns.
    *   **Short:** Converse conditions at Upper BB / range resistance.

*   **2.6 Exit Conditions:**
    *   **Stop-Loss:** Placed just beyond the identified range boundary (e.g., N x ATR below support for long).
    *   **Take-Profit:** Typically target the Bollinger Band midline or the opposite side of the range. May use smaller, fixed TP targets.
    *   **Range Breakout:** If price decisively breaks out of the LLM-confirmed range (monitored by Analyst Agent), exit immediately as strategy premise is void.

*   **2.7 Position Sizing (Preliminary):**
    *   Often uses fixed position sizes or sizes appropriate for higher win-rate, lower RRR trades.

*   **2.8 Implementation in Agent Framework:**
    *   Similar workflow to LTECS: User (via SOA) configures/launches LARIMERS Analyst (AA_LARIMERS) and Trader (TA_Main).
    *   **AA_LARIMERS:** Focuses its LLM on identifying valid ranging conditions and confirming reversal signals at boundaries. Dispatches signals to TA_Main.
    *   **TA_Main:** Validates LARIMERS signals against its historical performance data for that symbol under similar ranging conditions before execution.