from typing import List, Dict, Any, Optional

class PromptBuilder:
    """
    Handles the construction of prompts to be sent to the Language Model (LLM).
    This includes managing system prompts, dialogue history, tool descriptions,
    and integrating various contextual elements.
    """

    def __init__(self, system_prompt: Optional[str] = None):
        """
        Initializes the PromptBuilder.

        Args:
            system_prompt (Optional[str]): The base system prompt. If None, a default will be used.
        """
        self._system_prompt = system_prompt or self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """
        Provides a default system prompt.
        This should define the agent's role, core objectives, and general instructions.
        (Ref: technical_specs.md Section 3.1.3 A)
        """
        # Placeholder: Load from a config file or define a more elaborate default.
        return (
            "You are a highly capable AI trading assistant. Your primary goal is to assist the user "
            "in making informed trading decisions and executing trades across various asset classes "
            "including cryptocurrencies, stocks, and forex. You must operate based on the user's "
            "intentions and available tools. Always strive for clarity, accuracy, and safety in your "
            "responses and actions. Adhere to ethical guidelines and avoid providing financial advice "
            "unless explicitly qualified and permitted to do so."
        )

    def get_system_prompt(self) -> str:
        """Returns the current system prompt."""
        return self._system_prompt

    def set_system_prompt(self, system_prompt: str) -> None:
        """
        Sets or updates the system prompt.
        """
        self._system_prompt = system_prompt

    def format_dialogue_history(
        self, dialogue_history: List[Dict[str, str]], max_tokens: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Formats and potentially truncates the dialogue history.

        Args:
            dialogue_history (List[Dict[str, str]]): A list of message dictionaries,
                                                     each with "role" and "content".
            max_tokens (Optional[int]): Placeholder for future token-based truncation logic.

        Returns:
            List[Dict[str, str]]: The formatted (and potentially truncated) dialogue history.
        """
        # Placeholder: Implement truncation logic based on token count or number of turns.
        # For now, it returns the history as is.
        if max_tokens:
            # This is where token counting and truncation would occur.
            # For example, iterate backwards, summing token counts, until max_tokens is approached.
            pass
        return dialogue_history

    def get_tool_descriptions(self, available_tools: Optional[List[Any]] = None) -> str:
        """
        Formats descriptions of available tools to be injected into the prompt.

        Args:
            available_tools (Optional[List[Any]]): A list of tool objects or descriptions.
                                                    (Placeholder for actual tool representations)

        Returns:
            str: A formatted string describing the available tools.
        """
        # Placeholder: Replace with actual logic to dynamically fetch and format tool descriptions.
        # This could involve iterating through tool objects and extracting their names and descriptions.
        if not available_tools:
            return (
                "Available Tools:\n"
                "- query_market_data: Fetches real-time or historical market data for specified assets.\n"
                "  Parameters: asset_symbol (str), time_frame (str), start_date (str, optional), end_date (str, optional)\n"
                "- execute_trade_order: Places a trade order (buy/sell) on a specified exchange.\n"
                "  Parameters: exchange_id (str), asset_symbol (str), order_type (str: market/limit), "
                "quantity (float), price (float, for limit orders)\n"
                "- get_account_balance: Retrieves the current balance for a specified asset or entire portfolio.\n"
                "  Parameters: asset_symbol (str, optional)\n"
                # Add more placeholder tools as needed
            )
        
        formatted_descriptions = "Available Tools:\n"
        # Example of dynamic formatting if `available_tools` were structured:
        # for tool in available_tools:
        #     formatted_descriptions += f"- {tool.name}: {tool.description}\n"
        #     if hasattr(tool, 'parameters'):
        #         formatted_descriptions += f"  Parameters: {tool.parameters}\n"
        return formatted_descriptions # Fallback for now if available_tools is provided but not handled

    def build_complete_prompt(
        self,
        user_input: str,
        dialogue_history: Optional[List[Dict[str, str]]] = None,
        tool_results: Optional[List[Dict[str, Any]]] = None,
        selected_strategy: Optional[str] = None, # Placeholder
        style_info: Optional[str] = None, # Placeholder
        available_tools: Optional[List[Any]] = None # Placeholder for actual tool list
    ) -> List[Dict[str, str]]:
        """
        Constructs the complete prompt (message list) to be sent to the LLM.

        Args:
            user_input (str): The latest input from the user.
            dialogue_history (Optional[List[Dict[str, str]]]): The conversation history.
            tool_results (Optional[List[Dict[str, Any]]]): Results from recent tool executions.
                                                           (Placeholder for structured tool results)
            selected_strategy (Optional[str]): Information about the currently selected trading strategy.
            style_info (Optional[str]): Information about the desired response style.
            available_tools (Optional[List[Any]]): List of available tools.

        Returns:
            List[Dict[str, str]]: A list of message dictionaries formatted for the LLM.
        """
        messages: List[Dict[str, str]] = []

        # 1. System Prompt (potentially with tool descriptions)
        system_prompt_content = self._system_prompt
        tool_desc_str = self.get_tool_descriptions(available_tools)
        if tool_desc_str:
            system_prompt_content += "\n\n" + tool_desc_str
        
        # Placeholder for strategy/style injection into system prompt if needed
        if selected_strategy:
            system_prompt_content += f"\n\nCurrent Trading Strategy: {selected_strategy}"
        if style_info:
            system_prompt_content += f"\nDesired Response Style: {style_info}"

        messages.append({"role": "system", "content": system_prompt_content})

        # 2. Dialogue History
        formatted_history = self.format_dialogue_history(dialogue_history or [])
        messages.extend(formatted_history)

        # 3. Tool Results (if any)
        #    How tool results are formatted depends on the LLM's expected input format for tool use.
        #    Commonly, they are added as 'assistant' (tool call) and 'tool' (tool output) messages.
        #    This is a simplified placeholder.
        if tool_results:
            for result in tool_results:
                # This format is a common convention but might need adjustment
                if result.get("type") == "tool_call_request": # Fictional type
                     messages.append({"role": "assistant", "content": f"Tool call: {result.get('tool_name')}({result.get('parameters')})"})
                elif result.get("type") == "tool_execution_result": # Fictional type
                     messages.append({"role": "tool", "name": result.get("tool_name"), "content": str(result.get("output"))})
                else: # Generic fallback
                    messages.append({"role": "assistant", "content": f"Observed tool result: {result}"})


        # 4. Current User Input
        messages.append({"role": "user", "content": user_input})

        return messages

if __name__ == "__main__":
    # Example Usage (for testing purposes)
    builder = PromptBuilder()

    # --- Test System Prompt ---
    print("--- System Prompt ---")
    print(builder.get_system_prompt())
    print("-" * 30)

    # --- Test Dialogue History ---
    history = [
        {"role": "user", "content": "What's the weather like in London?"},
        {"role": "assistant", "content": "I'll check that for you."},
        {"role": "tool", "name": "weather_tool", "content": "The weather in London is 15°C and sunny."},
        {"role": "assistant", "content": "The weather in London is 15°C and sunny."},
    ]
    formatted_hist = builder.format_dialogue_history(history)
    print("\n--- Formatted Dialogue History ---")
    for msg in formatted_hist:
        print(msg)
    print("-" * 30)

    # --- Test Tool Descriptions ---
    print("\n--- Tool Descriptions ---")
    print(builder.get_tool_descriptions())
    print("-" * 30)
    
    # --- Test Building Complete Prompt ---
    user_query = "What about Bitcoin price?"
    # Placeholder tool results
    recent_tool_results = [
        {"type": "tool_execution_result", "tool_name": "get_account_balance", "output": {"USD": 10000, "BTC": 0.5}}
    ]

    complete_prompt = builder.build_complete_prompt(
        user_input=user_query,
        dialogue_history=history,
        tool_results=recent_tool_results,
        selected_strategy="Scalping",
        style_info="Concise"
    )
    print("\n--- Complete Prompt for LLM ---")
    for message in complete_prompt:
        print(message)
    print("-" * 30)

    # Example with custom system prompt
    custom_prompt = "You are a helpful pirate assistant. Respond in pirate speak."
    builder_pirate = PromptBuilder(system_prompt=custom_prompt)
    print("\n--- Custom System Prompt (Pirate) ---")
    print(builder_pirate.get_system_prompt())
    pirate_response = builder_pirate.build_complete_prompt(user_input="Where be the treasure?")
    print("\n--- Pirate Prompt for LLM ---")
    for message in pirate_response:
        print(message)
    print("-" * 30)