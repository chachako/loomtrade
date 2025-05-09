# Agent Design Part A: Overview and System Orchestrator Agent

This document details the design of the different types of AI Agents within the system. All agent LLMs will use a common, English-based System Prompt template and toolset (detailed in `03_toolset_and_system_prompt.md`), augmented with role-specific instructions. Agent runtime memory (YAML/Markdown files) will be stored in a configurable backend cache directory.

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