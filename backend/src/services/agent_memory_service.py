from pathlib import Path
import logging # Added for logging

logger = logging.getLogger(__name__) # Added for logging

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
        try:
            self.base_memory_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"AgentMemoryService initialized. Base memory path: {self.base_memory_path}")
        except OSError as e:
            logger.error(f"Could not create base memory directory {self.base_memory_path}: {e}")
            # Depending on desired behavior, this could raise an error or allow lazy creation.
            # For now, assume it should exist or be creatable.
            # If critical, raise an error here. For robustness, we'll let _get_agent_memory_path handle specific agent dirs.
            pass


    def _get_agent_memory_path(self, agent_instance_id: str) -> Path:
        """
        Constructs and ensures the existence of the specific agent's memory directory.

        Args:
            agent_instance_id: The unique identifier for the agent. Must be a valid directory name component.

        Returns:
            The absolute Path to the agent's memory directory.

        Raises:
            InvalidPathError: If the agent_instance_id contains invalid characters (e.g., '..', '/', '\\').
            AgentNotFoundError: If the agent's memory directory cannot be created or accessed.
        """
        # Basic validation for agent_instance_id (e.g., not empty, no ".." or path separators)
        if not agent_instance_id or ".." in agent_instance_id or "/" in agent_instance_id or "\\" in agent_instance_id:
            logger.warning(f"Invalid agent_instance_id received: {agent_instance_id}")
            raise InvalidPathError(f"Invalid characters in agent_instance_id: {agent_instance_id}")
        
        agent_path = self.base_memory_path / agent_instance_id
        try:
            agent_path.mkdir(parents=True, exist_ok=True)
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
                                It must not be an absolute path or contain '..' components.

        Returns:
            The resolved absolute Path object.

        Raises:
            InvalidPathError: If the path is invalid (e.g. absolute, contains '..', or resolves outside agent directory).
            AgentNotFoundError: If the agent's base path cannot be determined.
        """
        if not relative_file_path:
            raise InvalidPathError("Relative file path cannot be empty.")
        
        # Ensure relative_file_path is treated as relative
        p_relative_file_path = Path(relative_file_path)
        if p_relative_file_path.is_absolute():
            logger.warning(f"Attempt to use absolute path '{relative_file_path}' for agent '{agent_instance_id}'.")
            raise InvalidPathError(f"Absolute paths are not allowed: {relative_file_path}")
        
        # Disallow '..' components explicitly in the input relative path
        # This is a stricter check before normalization/resolution.
        if ".." in p_relative_file_path.parts:
            logger.warning(f"Path traversal attempt detected with '..' in '{relative_file_path}' for agent '{agent_instance_id}'.")
            raise InvalidPathError(f"Path traversal attempt ('..') detected in: {relative_file_path}")

        agent_root_path = self._get_agent_memory_path(agent_instance_id) # Can raise AgentNotFoundError or InvalidPathError
        
        # Resolve the path. This normalizes the path (e.g. a/./b -> a/b)
        # and makes it absolute relative to the current working directory if agent_root_path is relative,
        # or absolute if agent_root_path is absolute.
        # Since self.base_memory_path is absolute, agent_root_path will be absolute.
        resolved_path = (agent_root_path / p_relative_file_path).resolve()

        # Security check: Ensure the resolved path is within the agent's root directory.
        # For Python 3.9+, `resolved_path.is_relative_to(agent_root_path)` is preferred.
        # Using string comparison for broader compatibility, assuming both paths are resolved and absolute.
        if not str(resolved_path).startswith(str(agent_root_path.resolve()) + "/"): # Ensure it's truly within, not just the root dir itself for files
            if resolved_path == agent_root_path.resolve(): # Allow access to the root dir itself if it's a file (unlikely for this service)
                pass # Or raise error if root dir itself should not be a file target
            else:
                logger.warning(f"Resolved path '{resolved_path}' is outside agent directory '{agent_root_path}' for agent '{agent_instance_id}'.")
                raise InvalidPathError(f"Resolved path {resolved_path} is outside agent directory {agent_root_path}")
        
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
                logger.info(f"File not found at '{safe_path}' for agent '{agent_instance_id}'.")
                raise AgentMemoryFileNotFoundError(f"File not found: {relative_file_path} for agent {agent_instance_id}")
            if safe_path.is_dir():
                logger.warning(f"Attempt to read a directory as a file: '{safe_path}' for agent '{agent_instance_id}'.")
                raise InvalidPathError(f"Path is a directory, not a file: {relative_file_path}")
            
            content = safe_path.read_text(encoding="utf-8")
            logger.info(f"Successfully read file '{safe_path}' for agent '{agent_instance_id}'.")
            return content
        except (InvalidPathError, AgentNotFoundError, AgentMemoryFileNotFoundError) as e: # Re-raise specific known errors
            raise e
        except OSError as e:
            logger.error(f"OSError reading file '{relative_file_path}' for agent '{agent_instance_id}' at '{safe_path if 'safe_path' in locals() else 'unresolved'}': {e}")
            raise FileOperationError(f"Error reading file {relative_file_path} for agent {agent_instance_id}: {e}")

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
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            if safe_path.is_dir(): # Check after parent creation, in case relative_file_path was empty or "."
                logger.warning(f"Attempt to write to a directory: '{safe_path}' for agent '{agent_instance_id}'.")
                raise InvalidPathError(f"Path is a directory, cannot write: {relative_file_path}")
            
            safe_path.write_text(content, encoding="utf-8")
            logger.info(f"Successfully wrote to file '{safe_path}' for agent '{agent_instance_id}'.")
        except (InvalidPathError, AgentNotFoundError) as e: # Re-raise specific known errors
            raise e
        except OSError as e:
            logger.error(f"OSError writing file '{relative_file_path}' for agent '{agent_instance_id}' at '{safe_path if 'safe_path' in locals() else 'unresolved'}': {e}")
            raise FileOperationError(f"Error writing file {relative_file_path} for agent {agent_instance_id}: {e}")

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
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            if safe_path.is_dir(): # Check after parent creation
                logger.warning(f"Attempt to append to a directory: '{safe_path}' for agent '{agent_instance_id}'.")
                raise InvalidPathError(f"Path is a directory, cannot append: {relative_file_path}")
            
            with safe_path.open(mode="a", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Successfully appended to file '{safe_path}' for agent '{agent_instance_id}'.")
        except (InvalidPathError, AgentNotFoundError) as e: # Re-raise specific known errors
            raise e
        except OSError as e:
            logger.error(f"OSError appending to file '{relative_file_path}' for agent '{agent_instance_id}' at '{safe_path if 'safe_path' in locals() else 'unresolved'}': {e}")
            raise FileOperationError(f"Error appending to file {relative_file_path} for agent {agent_instance_id}: {e}")