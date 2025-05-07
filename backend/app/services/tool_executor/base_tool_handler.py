from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseToolHandler(ABC):
    """
    Abstract base class for tool handlers.
    All specific market tool handlers should inherit from this class
    and implement the execute_tool method.
    """

    @abstractmethod
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a specific tool with the given parameters.

        Args:
            tool_name: The name of the tool to execute.
            parameters: A dictionary of parameters for the tool.

        Returns:
            A dictionary containing the result of the tool execution.
        
        Raises:
            NotImplementedError: If the tool is not implemented by the handler.
            Exception: For any other execution errors.
        """
        pass