# System Architecture Design

This document outlines the high-level architecture for the AI Trading Agent system.

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph "UI/UX (Frontend - Next.js with TypeScript & React 19)"
        direction LR
        WebAppUI[Web Application UI (Magic UI)]
        BFF[API Routes (Backend for Frontend)]
        WebSocketClient[WebSocket Client]

        WebAppUI --> BFF
        WebAppUI --> WebSocketClient
    end

    subgraph "Core (Backend - Python with FastAPI)"
        direction LR
        APIServer[API Server (FastAPI)]
        SystemOrchestratorAgent[System Orchestrator Agent (LLM-Powered NLU & Task Dispatch)]
        AgentManager[Agent Manager (Lifecycle & Customization)]
        StrategyEngine[Strategy Engine (Execution for Specialized Agents)]
        ToolExecutor[Tool Executor (XML-based)]
        AgentMemoryService[Agent Memory Service (Agent YAML/Markdown in Cache)]
        ExchangeConnector[Exchange Connector (Binance First)]
        NotificationService[Notification Service (Incl. Telegram)]
        TaskScheduler[Background Task Scheduler (e.g., APScheduler/Celery)]
        WebSocketServer[WebSocket Server (FastAPI)]
        ConfigService[Configuration Service (API Keys, etc.)]

        APIServer --> SystemOrchestratorAgent
        APIServer --> ConfigService
        SystemOrchestratorAgent -- Interprets User NL --> SystemOrchestratorAgent
        SystemOrchestratorAgent -- Dispatches Tasks/Creates Agents --> AgentManager
        SystemOrchestratorAgent -- May Directly Use --> ToolExecutor
        AgentManager --> StrategyEngine
        AgentManager --> ToolExecutor
        AgentManager --> AgentMemoryService
        StrategyEngine --> ToolExecutor
        ToolExecutor --> ExchangeConnector
        ToolExecutor --> AgentMemoryService
        AgentMemoryService -- Reads/Writes --> FileSystemCache[Agent Memory Cache Directory]
        ExchangeConnector -- API Calls --> Binance[Binance API]
        TaskScheduler -- Triggers Agents/Tasks --> AgentManager
        TaskScheduler -- Triggers Agents/Tasks --> SystemOrchestratorAgent
        NotificationService -- Sends Alerts --> ExternalChannels[External Channels (e.g., Telegram)]
        SystemOrchestratorAgent --> NotificationService
        AgentManager --> NotificationService
        WebSocketServer -- Pushes Data --> WebSocketClient
        APIServer --> WebSocketServer
    end

    subgraph "Data and Configuration Storage"
        AppConfig[Application Configuration (Environment Variables, Secure Vaults for secrets)]
        AgentMemoryFileSystemCache[Agent-Specific Memory (YAML/Markdown in Cache Directory)]
        GlobalMemoryBankFileSystem[Global Project Memory Bank (/.roo/memory-bank/)]
    end

    BFF --> APIServer
    WebSocketClient --> WebSocketServer

    %% Styling
    classDef frontend fill:#D6EAF8,stroke:#3498DB,stroke-width:2px;
    classDef backend fill:#D5F5E3,stroke:#2ECC71,stroke-width:2px;
    classDef storage fill:#FCF3CF,stroke:#F1C40F,stroke-width:2px;
    classDef external fill:#EBDEF0,stroke:#8E44AD,stroke-width:2px;

    class WebAppUI,BFF,WebSocketClient frontend;
    class APIServer,SystemOrchestratorAgent,AgentManager,StrategyEngine,ToolExecutor,AgentMemoryService,ExchangeConnector,NotificationService,TaskScheduler,WebSocketServer,ConfigService backend;
    class AppConfig,AgentMemoryFileSystemCache,GlobalMemoryBankFileSystem storage;
    class Binance,FileSystemCache,ExternalChannels external;
```

## 2. Module Responsibilities

### 2.1 User Interface (Frontend - Next.js)
*   **`WebAppUI`**: Responsible for all user interaction interfaces, built with React 19 and Magic UI. Displays market data, Agent status, trading history, configuration interfaces, and the chat interface for interacting with the System Orchestrator Agent.
    *   Includes an **Onboarding/Setup Page** for first-time users or when critical configurations are missing. This page facilitates:
        *   Selection/confirmation of the trading market and provider (MVP: Binance Futures, pre-selected).
        *   Secure input and validation of LLM API Key(s).
        *   Secure input and validation of Exchange API Key(s).
    *   Access to the main application features is contingent upon successful completion of this initial setup.
*   **`BFF (API Routes)`**: Acts as a Backend for Frontend, handling some frontend logic, aggregating backend API calls, and simplifying frontend data requests.
*   **`WebSocketClient`**: Establishes and manages the WebSocket connection with the backend WebSocket server to receive real-time data updates.

### 2.2 Core Backend Services (Backend - Python with FastAPI)
*   **`APIServer`**: Provides RESTful API endpoints for the frontend (BFF or direct calls) to handle user requests, agent control, and other system interactions.
*   **`SystemOrchestratorAgent`**:
    *   The primary entry point for user natural language instructions.
    *   Utilizes LLM for NLU to understand user intent (e.g., define strategies, create/manage agents, execute tasks, set up monitoring).
    *   Parses natural language strategies into structured configurations or action sequences.
    *   Orchestrates tasks by interacting with `AgentManager`, `ToolExecutor`, `TaskScheduler`, or by directly invoking tools for simple requests.
    *   Follows an Agentic Loop for its own operations.
*   **`AgentManager`**:
    *   Manages the lifecycle of specialized agent instances (Analyst, Trader, etc.), including dynamic creation, configuration (based on input from System Orchestrator Agent), starting, pausing, and stopping.
    *   Implements agent permission controls.
    *   Facilitates inter-agent communication if needed (though direct message passing or shared context via memory might be more common).
*   **`StrategyEngine`**: Embedded within specialized Analyst Agents, this component is responsible for executing the logic of the defined trading strategies (e.g., evaluating indicator conditions, applying LLM-driven analytical rules).
*   **`ToolExecutor`**:
    *   Receives XML-formatted tool call requests from any LLM-powered agent (System Orchestrator, Analyst, Trader).
    *   Validates parameters and executes the corresponding tool logic (e.g., calling exchange APIs, calculating indicators, accessing agent memory).
*   **`AgentMemoryService`**:
    *   Manages read/write access to agent-specific memory files (YAML/Markdown) stored in a designated backend **cache directory** (e.g., `{app_cache_dir}/agent_memory/{agent_instance_id}/`).
    *   Provides an API for agents (via `ToolExecutor`) to interact with their memory.
*   **`ExchangeConnector`**: Encapsulates all interaction logic with exchange APIs (Binance Futures पहला, future support for others). Handles API calls for market data, order placement, account information, etc.
*   **`NotificationService`**: Manages and sends notifications to users through various configured channels (e.g., UI alerts, Telegram). Triggered by agents or system events.
*   **`TaskScheduler`**: Manages and executes background jobs, such as periodic market scanning by Analyst Agents or scheduled tasks defined by the user through the System Orchestrator Agent. Uses libraries like APScheduler or Celery.
*   **`WebSocketServer`**: Implemented within FastAPI, handles real-time bidirectional communication with connected frontend clients, pushing updates like market data, agent logs, trade execution confirmations, etc.
*   **`ConfigService`**: Manages and securely stores application-level configurations, including user-provided exchange API keys and LLM API keys.

### 2.3 Data & Configuration Storage
*   **`AppConfig`**: Stores application-level settings, environment variables, and provides access to securely stored secrets (e.g., master encryption keys, database credentials if used beyond agent memory).
*   **`AgentMemoryFileSystemCache`**: The file system location (a configurable cache directory on the backend server) where individual agent instances store their operational memory (logs, beliefs, trade history, etc.) in YAML or Markdown format.
*   **`GlobalMemoryBankFileSystem`**: The `/.roo/memory-bank/` directory used by the Project Manager mode for storing project-level documentation, plans, and global context.

## 3. Technology Stack Summary
*   **Frontend:** TypeScript, React 19, Next.js (with API Routes as BFF), pnpm (package manager), ESLint (linter), Magic UI (UI library).
*   **Backend:** Python, FastAPI, uv (package manager), Ruff (linter).
*   **Agent Memory:** YAML/Markdown files in a backend cache directory.
*   **Task Scheduling:** APScheduler or Celery (to be decided based on complexity).
*   **Primary Exchange (MVP):** Binance (Contracts).