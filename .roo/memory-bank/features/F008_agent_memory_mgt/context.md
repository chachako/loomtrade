# Feature Context: Agent 记忆库管理 (Agent Memory Management) (ID: F008_agent_memory_mgt)
*Initialized by Feature-Lead on 2025-05-10 12:30:15*
*Updated by Feature-Lead on 2025-05-10 12:33:45*

## 1. Overview & Goal
本功能的核心目标是实现一个 MemoryBankManager 模块，该模块为各个专用 Agent (如分析师 Agent、交易员 Agent) 提供持久化和检索其独立记忆内容的能力。
主要功能需求包括：
1.  为每个 Agent 实例提供一个独立的、基于文件系统的存储区域（例如，在后端的特定缓存或数据目录下，路径结构可能包含 Agent ID）。
2.  支持 Agent 以结构化格式（如 YAML 或 Markdown）读取和写入其记忆文件。常见的记忆文件可能包括：`short_term_memory.md` (用于临时上下文), `long_term_knowledge.yaml` (用于持久化知识点), `trade_history.csv` (用于交易记录), `strategy_parameters.yaml` (特定策略配置) 等。
3.  确保文件操作的原子性和基本的数据完整性（例如，通过安全的写入操作避免文件损坏）。
4.  提供清晰的 API 供 Agent 调用以进行记忆的存取。
该模块对于 Agent 的学习、适应和个性化行为至关重要。

## 2. Detailed Requirements / User Stories
*   As an Agent (Analyst/Trader), I want to save my current working context (e.g., market observations, intermediate calculations) to a `short_term_memory.md` file, so that I can resume my task later or if interrupted.
*   As an Agent, I want to load my working context from `short_term_memory.md` when I initialize or resume, so that I have the necessary information to proceed.
*   As an Agent, I want to store key learnings, successful parameters, or insights into a `long_term_knowledge.yaml` file, so that I can build a persistent knowledge base.
*   As an Agent, I want to retrieve specific knowledge from `long_term_knowledge.yaml` based on a key or query, so that I can leverage past learnings in new situations.
*   As a Trader Agent, I want to append every trade execution detail to `trade_history.csv`, so that I have a complete auditable record of my trading activity.
*   As an Agent, I want to read my specific `strategy_parameters.yaml` file, so that I can operate based on my assigned configuration.
*   As a System Orchestrator Agent (or an Agent with sufficient permissions), I want to list available memory files for a specific agent instance, so that I can understand its current memory state.
*   As a Backend Developer (integrating `MemoryBankManager`), I want a clear API to write data to a specified agent's memory file, ensuring the path is correctly resolved and the file is written atomically.
*   As a Backend Developer, I want a clear API to read data from a specified agent's memory file.

## 3. Acceptance Criteria
*   **AC1 (Write Memory):** Given an agent ID, a memory file name (e.g., `short_term_memory.md`), and content (string), When the `MemoryBankManager.write_memory()` API is called, Then the content is successfully written to the file at `{app_cache_dir}/agent_memory/{agent_id}/{memory_file_name}`, and the operation returns success.
*   **AC2 (Read Memory):** Given an agent ID and a memory file name, When the `MemoryBankManager.read_memory()` API is called, Then the content of the file is returned as a string, or an appropriate error (e.g., file not found) is raised.
*   **AC3 (Directory Structure):** Given an agent ID, When memory operations are performed for this agent, Then all its memory files are stored within a unique directory: `{app_cache_dir}/agent_memory/{agent_id}/`.
*   **AC4 (File Atomicity - Basic):** Given a write operation, When the operation is in progress, Then the system ensures that incomplete writes do not corrupt existing files (e.g., by writing to a temporary file then renaming).
*   **AC5 (Supported File Types - Initial):** The `MemoryBankManager` must support reading/writing plain text for `.md`, structured data for `.yaml` (parsing/serializing YAML), and row-based data for `.csv` (basic read/append).
*   **AC6 (API Definition):** The `MemoryBankManager` Python module provides clear, well-documented public methods for `read_memory(agent_id: str, file_name: str) -> str`, `write_memory(agent_id: str, file_name: str, content: str, mode: str = 'w') -> bool`, `append_to_memory(agent_id: str, file_name: str, content: str) -> bool` (especially for CSV), and `list_memory_files(agent_id: str) -> list[str]`.

## 4. Scope
### 4.1. In Scope:
*   Providing file-based storage for individual agent instances.
*   API for reading, writing, appending, and listing memory files (MD, YAML, CSV).
*   Ensuring agent-specific directory structure: `{app_cache_dir}/agent_memory/{agent_id}/`.
*   Basic atomic write operations (e.g., write-to-temp then rename).
*   Error handling for file operations (file not found, permission issues if applicable at this level).
### 4.2. Out of Scope:
*   In-memory caching layer on top of the file system (can be a future enhancement).
*   Complex database-backed memory storage.
*   Real-time synchronization of memory across multiple backend instances (if the backend scales horizontally, this needs more thought, but for MVP, assume single backend instance or non-shared cache for agents).
*   Memory encryption beyond file system permissions.
*   Semantic search or complex querying within memory files (agents are responsible for their own content interpretation).
*   Management of a "global" shared memory bank accessible by multiple agents simultaneously with fine-grained locking (primary focus is individual agent memory).

## 5. Technical Notes / Assumptions
*   The `MemoryBankManager` will be a Python module used by backend services, primarily invoked via the `ToolExecutor`.
*   The base path `{app_cache_dir}` for agent memories will be configurable (e.g., via environment variable or application config). This refers to a local directory on the backend server.
*   Agent IDs (`agent_id`) are unique strings.
*   File names will be provided by the agent (e.g., `short_term_memory.md`). Allowed characters in file names should be restricted to prevent path traversal issues.
*   Error handling should be robust, returning clear error messages or raising specific exceptions that can be handled by the `ToolExecutor` / calling agent.
*   Concurrency: For MVP, assume that a single agent instance's operations on its own memory files are serialized or infrequent enough not to cause major issues. If multiple threads/processes *within the same agent* try to write to the same file simultaneously, specific locking mechanisms might be needed at the `MemoryBankManager` level for those operations (e.g., file-level locks for write/append), or the agent itself must manage this.
*   Cross-agent memory access is out of scope for the `MemoryBankManager`'s direct responsibilities, but it should not prevent higher-level modules from implementing such logic if needed by reading/writing to known agent memory locations (respecting permissions managed elsewhere, as detailed below).

## 6. Agent Permissions for Memory Access
*User clarification: This agent memory bank is distinct from the Feature Lead's internal memory bank and resides in a local backend directory.*
### 6.1. Storage & Configuration of Permissions:
*   Permissions for each agent instance regarding its memory access (e.g., which files it can read/write, if it can list files) will be defined in its configuration.
*   This configuration is likely stored as a dedicated section within its main `agent_config.yaml` file, located in its specific memory directory (e.g., `{app_cache_dir}/agent_memory/{agent_instance_id}/agent_config.yaml`).
*   These configurations are initially set when an agent is created (e.g., by the `SystemOrchestratorAgent` based on user input or a template) and managed by the `AgentManager`.
*   Modifications to these permissions would also be routed through the `SystemOrchestratorAgent` / `AgentManager`.
### 6.2. Enforcement (by MemoryBankManager):
*   While the `AgentManager` is responsible for *setting* permissions, the `MemoryBankManager` itself might not directly enforce complex ACLs for MVP.
*   For MVP, the `MemoryBankManager` primarily ensures that an agent (identified by `agent_id`) can only operate within its own directory (`{app_cache_dir}/agent_memory/{agent_id}/`). It prevents path traversal.
*   More granular file-level read/write permissions within an agent's own directory, if needed beyond simple ownership, would be implicitly managed by the agent's own logic or defined in its `agent_config.yaml` and interpreted by the agent itself or a more sophisticated `ToolExecutor` layer before calling `MemoryBankManager`.
*   The `MemoryBankManager` API calls will always require the `agent_id` to scope the operation.
