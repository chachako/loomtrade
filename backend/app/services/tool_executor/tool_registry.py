from typing import Dict, Type
from .base_tool_handler import BaseToolHandler
from .crypto_handler import CryptoToolHandler
from .stock_handler import StockToolHandler # Optional, as per user request

# Initialize handlers
# In a more complex scenario, these might be initialized with configurations
crypto_handler_instance = CryptoToolHandler()
stock_handler_instance = StockToolHandler() # Optional

# Registry mapping market_type to handler instances
TOOL_HANDLERS: Dict[str, BaseToolHandler] = {
    "crypto": crypto_handler_instance,
    "stock": stock_handler_instance, # Example for stock market
    # Add other market types and their handlers here
    # e.g., "forex": ForexToolHandler()
}

def get_tool_handler(market_type: str) -> BaseToolHandler | None:
    """
    Retrieves a tool handler for the given market type.

    Args:
        market_type: The type of the market (e.g., "crypto", "stock").

    Returns:
        An instance of BaseToolHandler if found, otherwise None.
    """
    return TOOL_HANDLERS.get(market_type.lower())