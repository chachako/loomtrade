# Design Notes: Agent Memory Service (ID: agent_memory_service)
*Initialized by Feature-Lead on 2025-05-12 00:22:31*
*This document will be populated by relevant Coder modes during design sub-tasks and reviewed by Feature-Lead.*

## 1. API Design
The `AgentMemoryService` will be implemented as a Python class. It provides methods for the `ToolExecutor` to manage agent-specific memory files.

**Class Definition:**

```python
from pathlib import Path

class AgentMemoryError(Exception):
    """Base exception for AgentMemoryService errors."""
    pass

class AgentNotFoundError(AgentMemoryError):
    """Raised when an agent_instance_id is invalid or its directory cannot be processed."""
    pass

class AgentMemoryFileNotFoundError(AgentMemoryError): # Renamed to avoid conflict with built-in
    """Raised when a file is not found during a read operation."""
    pass

class InvalidPathError(AgentMemoryError):
    """Raised for invalid paths or directory traversal attempts."""
    pass

class FileOperationError(AgentMemoryError):
    """Raised for general file operation errors (e.g., permissions)."""
    pass

class AgentMemoryService:
    def __init__(self, app_cache_dir: str):
        """
        Initializes the AgentMemoryService.

        Args:
            app_cache_dir: The root directory for all agent memory storage.
        """
        self.base_memory_path = Path(app_cache_dir) / "agent_memory"
        # Potentially create self.base_memory_path if it doesn't exist,
        # though this might be better handled by the application setup.
        # For now, assume it exists or can be created by _get_agent_memory_path.

    def _get_agent_memory_path(self, agent_instance_id: str) -> Path:
        """
        Constructs and ensures the existence of the specific agent's memory directory.

        Args:
            agent_instance_id: The unique identifier for the agent.

        Returns:
            The absolute Path to the agent's memory directory.

        Raises:
            AgentNotFoundError: If the agent_instance_id is invalid or directory creation fails.
        """
        # Basic validation for agent_instance_id (e.g., not empty, no ".." or "/")
        if not agent_instance_id or ".." in agent_instance_id or "/" in agent_instance_id or "\\" in agent_instance_id:
            raise InvalidPathError(f"Invalid agent_instance_id: {agent_instance_id}")
        
        agent_path = self.base_memory_path / agent_instance_id
        try:
            agent_path.mkdir(parents=True, exist_ok=True)
            return agent_path
        except OSError as e:
            # Log the error e
            raise AgentNotFoundError(f"Could not create or access agent memory directory for {agent_instance_id}: {e}")

    def _resolve_safe_path(self, agent_instance_id: str, relative_file_path: str) -> Path:
        """
        Resolves a relative file path to an absolute path within the agent's memory directory,
        ensuring it's safe and does not traverse outside this directory.

        Args:
            agent_instance_id: The unique identifier for the agent.
            relative_file_path: The relative path to the file within the agent's memory.

        Returns:
            The resolved absolute Path object.

        Raises:
            InvalidPathError: If the path is invalid, attempts traversal, or is absolute.
            AgentNotFoundError: If the agent's base path cannot be determined.
        """
        if Path(relative_file_path).is_absolute():
            raise InvalidPathError(f"Absolute paths are not allowed: {relative_file_path}")
        if ".." in Path(relative_file_path).parts:
            raise InvalidPathError(f"Path traversal attempt detected: {relative_file_path}")

        agent_root_path = self._get_agent_memory_path(agent_instance_id)
        
        # Normalize the relative path to remove redundant separators or "."
        # os.path.normpath might be an option, but Path objects handle this well.
        # Path.resolve() also normalizes, but we want to ensure it's within agent_root_path
        
        resolved_path = (agent_root_path / relative_file_path).resolve()

        # Final check to ensure the resolved path is still within the agent's directory
        if agent_root_path not in resolved_path.parents and resolved_path != agent_root_path:
             # This check is crucial. resolved_path.relative_to(agent_root_path) would also work
             # but can throw ValueError if not a subpath.
             # A more robust check:
            if not str(resolved_path).startswith(str(agent_root_path)):
                 raise InvalidPathError(f"Resolved path {resolved_path} is outside agent directory {agent_root_path}")
        
        # Ensure the parent directory for the file exists if we are about to write/append
        # This is more relevant for write/append operations, but good to resolve here.
        # resolved_path.parent.mkdir(parents=True, exist_ok=True) # Do this in write/append

        return resolved_path

    def read_memory_file(self, agent_instance_id: str, relative_file_path: str) -> str:
        """
        Reads the content of a file from the agent's memory.

        Args:
            agent_instance_id: The unique identifier for the agent.
            relative_file_path: The relative path to the file.

        Returns:
            The content of the file as a string.

        Raises:
            AgentMemoryFileNotFoundError: If the file does not exist.
            InvalidPathError: If the path is invalid.
            FileOperationError: For other file reading issues.
            AgentNotFoundError: If agent path cannot be resolved.
        """
        try:
            safe_path = self._resolve_safe_path(agent_instance_id, relative_file_path)
            if not safe_path.exists():
                raise AgentMemoryFileNotFoundError(f"File not found: {relative_file_path} for agent {agent_instance_id}")
            if safe_path.is_dir():
                raise InvalidPathError(f"Path is a directory, not a file: {relative_file_path}")
            return safe_path.read_text(encoding="utf-8")
        except (InvalidPathError, AgentNotFoundError, AgentMemoryFileNotFoundError) as e: # Re-raise specific known errors
            raise e
        except OSError as e:
            # Log error e
            raise FileOperationError(f"Error reading file {relative_file_path} for agent {agent_instance_id}: {e}")

    def write_memory_file(self, agent_instance_id: str, relative_file_path: str, content: str) -> None:
        """
        Writes (or overwrites) content to a file in the agent's memory.

        Args:
            agent_instance_id: The unique identifier for the agent.
            relative_file_path: The relative path to the file.
            content: The string content to write.

        Raises:
            InvalidPathError: If the path is invalid.
            FileOperationError: For file writing issues.
            AgentNotFoundError: If agent path cannot be resolved.
        """
        try:
            safe_path = self._resolve_safe_path(agent_instance_id, relative_file_path)
            # Ensure parent directory exists before writing
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            if safe_path.is_dir():
                raise InvalidPathError(f"Path is a directory, cannot write: {relative_file_path}")
            safe_path.write_text(content, encoding="utf-8")
        except (InvalidPathError, AgentNotFoundError) as e: # Re-raise specific known errors
            raise e
        except OSError as e:
            # Log error e
            raise FileOperationError(f"Error writing file {relative_file_path} for agent {agent_instance_id}: {e}")

    def append_to_memory_file(self, agent_instance_id: str, relative_file_path: str, content: str) -> None:
        """
        Appends content to a file in the agent's memory. Creates the file if it doesn't exist.

        Args:
            agent_instance_id: The unique identifier for the agent.
            relative_file_path: The relative path to the file.
            content: The string content to append.

        Raises:
            InvalidPathError: If the path is invalid.
            FileOperationError: For file appending issues.
            AgentNotFoundError: If agent path cannot be resolved.
        """
        try:
            safe_path = self._resolve_safe_path(agent_instance_id, relative_file_path)
            # Ensure parent directory exists before appending
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            if safe_path.is_dir():
                raise InvalidPathError(f"Path is a directory, cannot append: {relative_file_path}")
            with safe_path.open(mode="a", encoding="utf-8") as f:
                f.write(content)
        except (InvalidPathError, AgentNotFoundError) as e: # Re-raise specific known errors
            raise e
        except OSError as e:
            # Log error e
            raise FileOperationError(f"Error appending to file {relative_file_path} for agent {agent_instance_id}: {e}")

```

**Key Design Considerations from Context:**
*   **Path Validation:** Implemented in `_resolve_safe_path` to prevent directory traversal using `Path.resolve()` and checking if the resolved path is within the agent's designated root memory path. It also checks for `..` in paths and absolute paths. `agent_instance_id` is also validated.
*   **Error Handling:** Custom exceptions (`AgentMemoryError`, `AgentNotFoundError`, `AgentMemoryFileNotFoundError`, `InvalidPathError`, `FileOperationError`) are defined for clear error communication.
*   **Directory Creation:** The agent's specific memory directory (`{app_cache_dir}/agent_memory/{agent_instance_id}/`) is created if it doesn't exist by `_get_agent_memory_path` (called by `_resolve_safe_path`). Parent directories for files are created by `write_memory_file` and `append_to_memory_file` before file operations.
*   **File Encoding:** UTF-8 is used for all file operations (`read_text`, `write_text`, `open`).
*   **Idempotency:** `_get_agent_memory_path` and directory creation within write/append methods are idempotent (`exist_ok=True`).

This design addresses the core requirements for reading, writing, and appending files, with a strong emphasis on security and error handling.

## 2. UI/UX High-Level Design Notes
*(Key UI components, user flows, wireframe references, state management considerations for frontend features. Likely N/A for this backend service, but section kept for consistency.)*
N/A for this backend service.

## 3. Key Data Structures / Models
*(Important data models or structures specific to this feature, beyond global models. E.g., structure for representing file paths, content, or operation status.)*
*   `pathlib.Path` is used extensively for path manipulation and validation.
*   Method arguments and return types are standard Python types (str, None).
*   Custom exception classes as defined in the API Design section.

## 4. Other Technical Design Considerations
*(E.g., specific algorithms, third-party service integration details, non-functional requirements impacting design, error handling strategies, file locking mechanisms if concurrent access is a concern.)*
*   **Security:** Path traversal is the primary security concern addressed. `_resolve_safe_path` is critical.
*   **Logging:** Basic logging should be added within the methods, especially for error conditions and significant operations (e.g., "File X written for agent Y"). This is not explicitly shown in the signatures but is assumed.
*   **Concurrency:** This design assumes single-process access or that concurrency is managed at a higher level. File locking is not implemented and is out of scope per `context.md`.
*   **Configuration:** `app_cache_dir` is configurable via the constructor.
*   **Atomicity:** File operations rely on OS-level atomicity for single read/write/append calls.