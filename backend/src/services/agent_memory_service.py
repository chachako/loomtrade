from pathlib import Path
import logging # Added for logging

# Configure basic logging
# In a real application, logging would be configured more centrally.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentMemoryError(Exception):
    """Base exception for AgentMemoryService errors."""
    pass

class AgentNotFoundError(AgentMemoryError):
    """Raised when an agent_instance_id is invalid or its directory cannot be processed."""
    pass

class AgentMemoryFileNotFoundError(AgentMemoryError):
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
        logger.info(f"AgentMemoryService initialized with base_memory_path: {self.base_memory_path}")
        # Ensure the base directory for all agent memories exists
        try:
            self.base_memory_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Base memory path {self.base_memory_path} ensured.")
        except OSError as e:
            logger.error(f"Could not create base memory directory {self.base_memory_path}: {e}")
            # This is a critical failure for the service, so re-raise appropriately
            # Or handle as per application's startup error handling strategy
            raise AgentMemoryError(f"Could not create base memory directory {self.base_memory_path}: {e}")


    def _get_agent_memory_path(self, agent_instance_id: str) -> Path:
        """
        Constructs and ensures the existence of the specific agent's memory directory.

        Args:
            agent_instance_id: The unique identifier for the agent.

        Returns:
            The absolute Path to the agent's memory directory.

        Raises:
            InvalidPathError: If the agent_instance_id contains invalid characters.
            AgentNotFoundError: If the agent's memory directory cannot be created or accessed.
        """
        if not agent_instance_id or ".." in agent_instance_id or "/" in agent_instance_id or "\\" in agent_instance_id:
            logger.warning(f"Invalid agent_instance_id received: {agent_instance_id}")
            raise InvalidPathError(f"Invalid agent_instance_id: {agent_instance_id}")
        
        agent_path = self.base_memory_path / agent_instance_id
        try:
            agent_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Agent memory path {agent_path} ensured for agent {agent_instance_id}.")
            return agent_path
        except OSError as e:
            logger.error(f"Could not create or access agent memory directory for {agent_instance_id} at {agent_path}: {e}")
            raise AgentNotFoundError(f"Could not create or access agent memory directory for {agent_instance_id}: {e}")

    def _resolve_safe_path(self, agent_instance_id: str, relative_file_path: str) -> Path:
        """
        Resolves a relative file path to an absolute path within the agent's memory directory,
        ensuring it's safe and does not traverse outside this directory.

        Args:
            agent_instance_id: The unique identifier for the agent.
            relative_file_path: The relative path to the file within the agent's memory.
                                Must not be empty or None.

        Returns:
            The resolved absolute Path object.

        Raises:
            InvalidPathError: If the path is invalid, attempts traversal, is absolute, or is empty.
            AgentNotFoundError: If the agent's base path cannot be determined.
        """
        if not relative_file_path:
            logger.warning(f"Empty relative_file_path received for agent {agent_instance_id}.")
            raise InvalidPathError("Relative file path cannot be empty.")

        # First, check if the original path string itself is absolute.
        if Path(relative_file_path).is_absolute():
            logger.warning(f"Absolute path received: {relative_file_path} for agent {agent_instance_id}.")
            raise InvalidPathError(f"Absolute paths are not allowed: {relative_file_path}")

        # Normalize by stripping leading slashes to handle user errors like "/subdir/file.txt"
        # which are intended to be relative to agent's root.
        normalized_relative_path_str = relative_file_path.lstrip('/')
        
        # After stripping, if it's *still* somehow absolute (e.g. "C:\foo" on Windows, or if lstrip was no-op for a non-/ absolute path)
        # This check is somewhat redundant if the first check is comprehensive, but adds a layer.
        if Path(normalized_relative_path_str).is_absolute():
            logger.warning(f"Path still treated as absolute after normalization: {normalized_relative_path_str} (original: {relative_file_path}) for agent {agent_instance_id}.")
            raise InvalidPathError(f"Paths must be relative: {relative_file_path}")

        # Check for ".." parts which indicate traversal attempts in the normalized string
        if ".." in Path(normalized_relative_path_str).parts:
            logger.warning(f"Path traversal attempt detected: {relative_file_path} for agent {agent_instance_id}.")
            raise InvalidPathError(f"Path traversal attempt detected: {relative_file_path}")

        agent_root_path = self._get_agent_memory_path(agent_instance_id)
        
        # Construct the path and resolve it.
        # (agent_root_path / normalized_relative_path_str) handles joining correctly.
        # .resolve() makes it absolute and canonical (removes . and .. if any slip through, though ".." is checked above)
        resolved_path = (agent_root_path / normalized_relative_path_str).resolve()

        # Final security check: ensure the resolved path is truly within the agent's root directory.
        # This is critical to prevent any clever path manipulation from escaping.
        if not str(resolved_path).startswith(str(agent_root_path.resolve())):
            logger.error(f"Path security violation: Resolved path {resolved_path} is outside agent directory {agent_root_path.resolve()} for agent {agent_instance_id}.")
            raise InvalidPathError(f"Resolved path {resolved_path} is outside agent directory {agent_root_path.resolve()}")
        
        logger.debug(f"Path resolved safely: {resolved_path} for agent {agent_instance_id}, relative path {relative_file_path}.")
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
            InvalidPathError: If the path is invalid or points to a directory.
            FileOperationError: For other file reading issues.
            AgentNotFoundError: If agent path cannot be resolved.
        """
        try:
            safe_path = self._resolve_safe_path(agent_instance_id, relative_file_path)
            if not safe_path.exists():
                logger.warning(f"File not found: {safe_path} for agent {agent_instance_id}.")
                raise AgentMemoryFileNotFoundError(f"File not found: {relative_file_path} for agent {agent_instance_id}")
            if safe_path.is_dir():
                logger.warning(f"Attempt to read a directory as a file: {safe_path} for agent {agent_instance_id}.")
                raise InvalidPathError(f"Path is a directory, not a file: {relative_file_path}")
            
            content = safe_path.read_text(encoding="utf-8")
            logger.info(f"Successfully read file {safe_path} for agent {agent_instance_id}.")
            return content
        except (InvalidPathError, AgentNotFoundError, AgentMemoryFileNotFoundError) as e:
            raise e # Re-raise specific known errors
        except OSError as e:
            logger.error(f"OSError reading file {relative_file_path} for agent {agent_instance_id} at {safe_path if 'safe_path' in locals() else 'unresolved path'}: {e}")
            raise FileOperationError(f"Error reading file {relative_file_path} for agent {agent_instance_id}: {e}")
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"Unexpected error reading file {relative_file_path} for agent {agent_instance_id}: {e}")
            raise AgentMemoryError(f"Unexpected error reading file {relative_file_path}: {e}")


    def write_memory_file(self, agent_instance_id: str, relative_file_path: str, content: str) -> None:
        """
        Writes (or overwrites) content to a file in the agent's memory.

        Args:
            agent_instance_id: The unique identifier for the agent.
            relative_file_path: The relative path to the file.
            content: The string content to write.

        Raises:
            InvalidPathError: If the path is invalid or points to a directory.
            FileOperationError: For file writing issues.
            AgentNotFoundError: If agent path cannot be resolved.
        """
        try:
            safe_path = self._resolve_safe_path(agent_instance_id, relative_file_path)
            
            # Ensure parent directory exists before writing
            try:
                safe_path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Parent directory {safe_path.parent} ensured for agent {agent_instance_id}.")
            except OSError as e:
                logger.error(f"Could not create parent directory {safe_path.parent} for agent {agent_instance_id}: {e}")
                raise FileOperationError(f"Could not create parent directory for {relative_file_path}: {e}")

            if safe_path.is_dir():
                logger.warning(f"Attempt to write to a directory: {safe_path} for agent {agent_instance_id}.")
                raise InvalidPathError(f"Path is a directory, cannot write: {relative_file_path}")
            
            safe_path.write_text(content, encoding="utf-8")
            logger.info(f"Successfully wrote to file {safe_path} for agent {agent_instance_id}.")
        except InvalidPathError as e_invalid_path:
            # Handles InvalidPathError from _resolve_safe_path or is_dir check
            raise e_invalid_path
        except AgentNotFoundError as e_agent_not_found:
            # Handles AgentNotFoundError from _resolve_safe_path
            raise e_agent_not_found
        except FileOperationError as e_file_op:
            # Handles FileOperationError explicitly raised from parent.mkdir's exception handling
            raise e_file_op
        except OSError as e_os_write: # Specifically for OSError from write_text or other direct OS calls
            err_msg = f"Error writing file {relative_file_path} for agent {agent_instance_id}: {e_os_write}"
            logger.error(f"OSError during write operation for {relative_file_path}, agent {agent_instance_id} at {safe_path if 'safe_path' in locals() else 'unresolved path'}: {e_os_write}")
            raise FileOperationError(err_msg)
        except Exception as e_general: # Catch any other unexpected errors
            err_msg = f"Unexpected error writing file {relative_file_path}: {e_general}"
            logger.error(f"Unexpected general error writing file {relative_file_path} for agent {agent_instance_id}: {e_general}")
            raise AgentMemoryError(err_msg)

    def append_to_memory_file(self, agent_instance_id: str, relative_file_path: str, content: str) -> None:
        """
        Appends content to a file in the agent's memory. Creates the file if it doesn't exist.

        Args:
            agent_instance_id: The unique identifier for the agent.
            relative_file_path: The relative path to the file.
            content: The string content to append.

        Raises:
            InvalidPathError: If the path is invalid or points to a directory.
            FileOperationError: For file appending issues.
            AgentNotFoundError: If agent path cannot be resolved.
        """
        try:
            safe_path = self._resolve_safe_path(agent_instance_id, relative_file_path)

            # Ensure parent directory exists before appending
            try:
                safe_path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Parent directory {safe_path.parent} ensured for agent {agent_instance_id}.")
            except OSError as e:
                logger.error(f"Could not create parent directory {safe_path.parent} for agent {agent_instance_id}: {e}")
                raise FileOperationError(f"Could not create parent directory for {relative_file_path}: {e}")

            if safe_path.is_dir():
                logger.warning(f"Attempt to append to a directory: {safe_path} for agent {agent_instance_id}.")
                raise InvalidPathError(f"Path is a directory, cannot append: {relative_file_path}")
            
            with safe_path.open(mode="a", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Successfully appended to file {safe_path} for agent {agent_instance_id}.")
        except InvalidPathError as e_invalid_path:
            # Handles InvalidPathError from _resolve_safe_path or is_dir check
            raise e_invalid_path
        except AgentNotFoundError as e_agent_not_found:
            # Handles AgentNotFoundError from _resolve_safe_path
            raise e_agent_not_found
        except FileOperationError as e_file_op:
            # Handles FileOperationError explicitly raised from parent.mkdir's exception handling
            raise e_file_op
        except OSError as e_os_append: # Specifically for OSError from open/write in append
            err_msg = f"Error appending to file {relative_file_path} for agent {agent_instance_id}: {e_os_append}"
            logger.error(f"OSError during append operation for {relative_file_path}, agent {agent_instance_id} at {safe_path if 'safe_path' in locals() else 'unresolved path'}: {e_os_append}")
            raise FileOperationError(err_msg)
        except Exception as e_general: # Catch any other unexpected errors
            err_msg = f"Unexpected error appending to file {relative_file_path}: {e_general}"
            logger.error(f"Unexpected general error appending to file {relative_file_path} for agent {agent_instance_id}: {e_general}")
            raise AgentMemoryError(err_msg)