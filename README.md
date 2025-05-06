# Loomtrade

[English](./README.md) | [简体中文](./README.zh-CN.md)

**Loomtrade** is a platform for designing, automating, and managing AI-driven trading agents for cryptocurrency futures. Users define strategies via natural language, and intelligent agents, powered by Large Language Models (LLMs), navigate market complexities.

## Key Features

*   🌐 **Natural Language Strategies:** Describe your trading ideas using natural language. Loomtrade translates them into actionable, automated strategies.
*   🤖 **Intelligent Agents:** Powered by advanced LLMs, agents understand strategies, analyze market data, make trading decisions, and manage positions.
*   🛠️ **Comprehensive Toolset:** Interact with exchanges and data sources via a robust set of tools for analysis, order execution, and account management.
*   📊 **Database-Driven Learning:** All trading activities, decisions, and market observations are stored, enabling agents to learn from experience and allowing for detailed user analysis.
*   ⚙️ **Customizable Styles & Risk Management:** Define preferred trading styles (e.g., conservative, aggressive, trend-following) and detailed risk parameters to align agent behavior with your risk appetite.
*   💬 **Interactive Monitoring & Control:** Chat with agents, issue commands, query decision rationale, and monitor activities in real-time via the dashboard.
*   📈 **TradingView Integration:** Visualize market data and agent actions on familiar TradingView charts.
*   🔍 **Transparent Operations:** Access detailed logs of agent "thoughts" (LLM interactions) and actions for full decision-making transparency.

## How It Works

Loomtrade operates on an **Agentic Loop** principle, where AI agents continuously:

1.  **Perceive:** Monitor market data (prices, indicators, order books) and user inputs/commands.
2.  **Reason:** Leverage LLMs to analyze perceived information against user-defined strategies and trading styles stored in its database memory. The LLM understands the database schema and can request specific data via tools.
3.  **Decide:** Based on reasoning, the LLM determines the next course of action – whether to call another tool for more data, execute a trade, adjust a position, or communicate with the user.
4.  **Act:** The agent executes the LLM's decision by calling appropriate tools (e.g., `create_order` for trades, `query_database` for historical data).
5.  **Learn (Reflect):** After significant trades, the LLM is prompted to reflect on outcomes, rationale, and market conditions. These reflections are stored in the database, forming a queryable experience base for future decisions.

This loop enables Loomtrade agents to operate autonomously, adapt to market changes based on strategy and learned experience, and execute trades with precision.

## Quick Start Guide

1.  **Sign Up:** Create your Loomtrade account on the website.
2.  **Connect Exchange:** Navigate to "Exchanges", select your cryptocurrency futures exchange (e.g., Binance, OKX), and securely enter your API Key/Secret (ensure trading permissions are enabled, withdrawals disabled for security).
3.  **Configure LLM Provider:** Go to "LLM Settings", choose your provider/model (e.g., OpenAI, Google Gemini), and enter your LLM API Key.
4.  **Define Your First AI Agent:**
    *   **Select Trading Style:** Choose a preset (e.g., "Cautious Trend Follower") or customize risk parameters.
    *   **Create Trading Strategy:** Use the natural language editor to define your trading approach. For example:
        *   For specific rules: `"If BTC 15min RSI is below 30 and MACD histogram is positive, open long with 2% capital. Set SL at 1.5x ATR and TP at 3x ATR."`
        *   For more autonomous delegation: `"Act as a cautious portfolio manager for my altcoin allocation. Scan the market every 1 hour for high-momentum, mid-cap altcoins. On strong bullish signals confirmed by at least two different indicators, enter with a small position (1-2% of sub-portfolio). Dynamically adjust take-profit based on trend strength and implement a trailing stop."`
    *   **Activate Agent:** Review settings and activate the Loomtrade agent.
5.  **Monitor & Interact:** Observe agent activity, P&L, and positions on the dashboard. Chat with the agent for updates or adjustments. Review the "Agent's Inner Monologue" tab for transparency.

## Use Cases

*   **Automate Day Trading Strategies:** Delegate execution discipline and speed for short-term trading to Loomtrade.
*   **Execute Complex Conditional Orders:** Define multi-condition entries and exits in natural language, surpassing basic exchange order types.
*   **Trend Following & Swing Trading:** Design agents to identify and capitalize on market trends over various periods.
*   **(Future Feature) Event-Driven Trading:** Configure agents to react to specific news or on-chain events.
*   **(Future Feature) Portfolio Rebalancing for Futures:** Automate rebalancing across multiple crypto futures contracts based on defined targets.

## ⚠️ Important Risk Disclosure

*   **Trading cryptocurrency futures is highly speculative and carries a substantial risk of loss.** It is not suitable for all investors. Only invest funds you can afford to lose.
*   **Past performance is not indicative of future results.** Any historical data or backtesting results presented by Loomtrade are for informational purposes only and do not guarantee future success.
*   **AI and LLMs are not infallible.** They can make mistakes, misinterpret data, or generate suboptimal decisions ("hallucinations"). Loomtrade provides transparency tools, but users are ultimately responsible for monitoring their agents and managing risk.
*   **Market conditions can change rapidly.** Automated systems may not always adapt perfectly to extreme volatility or unforeseen "black swan" events.
*   **Software bugs and connectivity issues can occur.** While we strive for a robust system, technical failures are possible.
*   **Always use Loomtrade responsibly and in accordance with your own risk tolerance and financial situation.** Consider starting with small amounts or paper trading.

## Tech Stack Overview (Planned)

*   **Frontend:** Modern JavaScript framework (e.g., React, Vue, or Svelte with TypeScript).
*   **Backend:** Node.js (TypeScript) or Python (e.g., FastAPI).
*   **Database:** PostgreSQL for structured data (configurations, trade history, agent memory).
*   **Real-time Communication:** WebSockets.
*   **Charting:** TradingView Lightweight Charts™ integration.

## Roadmap (Conceptual)

*   **V1.0 (MVP):** Core agent functionality, natural language strategy definition, key exchange integrations, dashboard monitoring, essential trading tools.
*   **V1.x:** Enhanced strategy builder, more indicators, expanded LLM support, improved risk management tools, detailed analytics.
*   **V2.0:** Strategy backtesting engine, advanced agent learning capabilities (database-driven reflection analysis), more sophisticated market scanning tools.

---

*This README provides a high-level overview. For detailed design specifications, please refer to the `blueprints/technical_specs.md` document.*