# Feature Context: Agent Memory Service (ID: agent_memory_service)
*Initialized by Feature-Lead on 2025-05-12 00:21:11*

## 1. Overview & Goal
Implement the AgentMemoryService, responsible for managing read/write access to agent-specific runtime memory files (YAML/Markdown) stored in a designated backend cache directory (e.g., {app_cache_dir}/agent_memory/{agent_instance_id}/). This service will provide an API (internally used by the ToolExecutor) for agents to interact with their memory. Key functionalities include reading files, writing/overwriting files, and appending to files. Refer to `00_system_architecture.md` for its role in the overall architecture and `03c_toolset_memory_and_orchestration.md` for the specifications of `read_agent_memory_file`, `write_agent_memory_file`, and `append_to_agent_memory_file` tools, which this service will effectively underpin.
*(Detailed goal to be refined by Feature-Lead during planning.)*

## 2. Detailed Requirements / User Stories
*   **User Story 1 (Read Memory):** As a `ToolExecutor`, I want to be able to represent an agent and read a file from its designated memory directory, so that the agent can access its previously stored information.
*   **User Story 2 (Write/Overwrite Memory):** As a `ToolExecutor`, I want to be able to represent an agent and write (or overwrite) a file in its designated memory directory, so that the agent can save or update its state/knowledge.
*   **User Story 3 (Append to Memory):** As a `ToolExecutor`, I want to be able to represent an agent and append content to an existing file (or create it if it doesn't exist) in its memory directory, so that the agent can progressively log information.

## 3. Acceptance Criteria
    *   **AC for User Story 1 (Read Memory):**
        *   Given an agent instance ID and a valid relative file path within the agent's memory directory,
        *   When the `read_agent_memory_file` operation is invoked by the `ToolExecutor` (via `AgentMemoryService`),
        *   Then the content of the specified file is returned successfully.
        *   Given an agent instance ID and a non-existent file path,
        *   When the `read_agent_memory_file` operation is invoked,
        *   Then an appropriate error (e.g., "file not found") is returned.
        *   Given an invalid agent instance ID,
        *   When any memory operation is invoked,
        *   Then an appropriate error (e.g., "agent not found" or "invalid agent ID") is returned.
        *   Given a file path that attempts to access outside the agent's designated memory directory (path traversal),
        *   When any memory operation is invoked,
        *   Then an appropriate security error (e.g., "access denied" or "invalid path") is returned.
    *   **AC for User Story 2 (Write/Overwrite Memory):**
        *   Given an agent instance ID, a valid relative file path, and content,
        *   When the `write_agent_memory_file` operation is invoked,
        *   Then the file is created/overwritten with the provided content in the agent's memory directory, and a success status is returned.
        *   Given a file path that attempts to access outside the agent's designated memory directory,
        *   When the `write_agent_memory_file` operation is invoked,
        *   Then an appropriate security error is returned and no file is written.
    *   **AC for User Story 3 (Append to Memory):**
        *   Given an agent instance ID, a valid relative file path, and content to append,
        *   When the `append_to_agent_memory_file` operation is invoked and the file exists,
        *   Then the new content is appended to the existing file in the agent's memory directory, and a success status is returned.
        *   Given an agent instance ID, a valid relative file path, and content to append,
        *   When the `append_to_agent_memory_file` operation is invoked and the file does not exist,
        *   Then the file is created with the provided content in the agent's memory directory, and a success status is returned.
        *   Given a file path that attempts to access outside the agent's designated memory directory,
        *   When the `append_to_agent_memory_file` operation is invoked,
        *   Then an appropriate security error is returned and no file is modified or created.

## 4. Scope
### 4.1. In Scope:
*   Implementation of the `AgentMemoryService` class/module.
*   Internal methods within `AgentMemoryService` to handle read, write/overwrite, and append operations for YAML and Markdown files.
*   Directory creation for `{app_cache_dir}/agent_memory/{agent_instance_id}/` if it doesn't exist upon first write/append.
*   Path validation to ensure operations are confined to the agent's specific memory directory.
*   Error handling for file operations (e.g., file not found, permission issues within its own directory).
*   Basic logging of service operations (e.g., file read, file written).
### 4.2. Out of Scope:
*   The `ToolExecutor` itself or the specific tools (`read_agent_memory_file`, `write_agent_memory_file`, `append_to_agent_memory_file`) that *use* this service. This service *underpins* them.
*   Management of the `{app_cache_dir}` itself (e.g., global cache eviction policies).
*   Advanced file management features like versioning, locking for concurrent agent access (beyond basic path safety), or transactional operations.
*   Content parsing or validation of YAML/Markdown files (service treats them as opaque text).
*   User interface for memory management.
*   Real-time synchronization of memory files if multiple system instances were to run (assume single instance context for now).

## 5. Technical Notes / Assumptions
*   The service will be implemented in Python, aligning with the primary language of the system.
*   The `{app_cache_dir}` will be a configurable path provided to the service during initialization.
*   `agent_instance_id` will be a string that is safe for use as a directory name.
*   File operations are assumed to be atomic at the OS level for single operations (read, write, append). Complex transactional safety across multiple operations is out of scope.
*   Error messages returned by the service should be clear and informative for the `ToolExecutor`.
*   The service will run as part of the main application process; no inter-process communication is initially assumed for this service itself.
*   Security: Path traversal prevention is a key security consideration. Input file paths from tools must be strictly validated and normalized to ensure they resolve within the designated agent memory directory.
*   File encoding will default to UTF-8.