from typing import Dict, Any
import logging

from .tool_registry import get_tool_handler
# Assuming ExchangeConfig might be used to determine market_type or pass specific exchange details
# from app.schemas.exchange_config import ExchangeConfig

logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Main class responsible for executing tools based on market type.
    It uses a registry to find the appropriate handler for a given market
    and delegates the tool execution to that handler.
    """

    async def execute(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        market_type: str,
        # exchange_config: ExchangeConfig | None = None # Optional: if needed for handler initialization or context
    ) -> Dict[str, Any]:
        """
        Executes the specified tool for the given market type.

        Args:
            tool_name: The name of the tool to execute.
            parameters: A dictionary of parameters for the tool.
            market_type: The type of market (e.g., "crypto", "stock") to determine the handler.
            exchange_config: Optional ExchangeConfig object if specific exchange details are needed.

        Returns:
            A dictionary containing the result of the tool execution or an error message.
        """
        logger.info(
            f"Attempting to execute tool '{tool_name}' for market_type '{market_type}' "
            f"with parameters: {parameters}"
        )

        handler = get_tool_handler(market_type)

        if not handler:
            logger.error(f"No tool handler found for market_type: {market_type}")
            return {
                "tool_name": tool_name,
                "status": "error",
                "message": f"No tool handler found for market_type: {market_type}"
            }

        try:
            # Here, you might pass exchange_config to the handler if it needs specific
            # API keys or endpoints, e.g., handler.set_exchange_config(exchange_config)
            # or pass it directly to execute_tool if the handler's method expects it.
            # For now, keeping it simple.
            result = await handler.execute_tool(tool_name, parameters)
            logger.info(f"Tool '{tool_name}' executed successfully. Result: {result}")
            return result
        except NotImplementedError as e:
            logger.error(f"Tool '{tool_name}' not implemented in handler for market_type '{market_type}': {e}")
            return {"tool_name": tool_name, "status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}' for market_type '{market_type}': {e}", exc_info=True)
            return {
                "tool_name": tool_name,
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}"
            }