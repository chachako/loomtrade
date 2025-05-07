import re
from typing import Any, Dict, Iterator, List

class LLMResponseParser:
    """
    Parses responses from an LLM, handling streaming data,
    thinking processes, and tool calls.
    """

    def __init__(self):
        self._buffer: str = ""
        self._thinking_tag_open: str = "<thinking>"
        self._thinking_tag_close: str = "</thinking>"
        self._tool_call_tag_open_regex: re.Pattern = re.compile(r"<([a-zA-Z0-9_]+)>") # Simplified for now
        self._tool_call_tag_close_regex: re.Pattern = re.compile(r"</([a-zA-Z0-9_]+)>") # Simplified for now
        self._current_tool_name: str | None = None
        self._tool_call_buffer: str = ""

    def _extract_thinking_content(self) -> Iterator[Dict[str, Any]]:
        """
        Extracts thinking blocks from the buffer.
        Yields thinking blocks if found and removes them from the buffer.
        """
        start_index = self._buffer.find(self._thinking_tag_open)
        while start_index != -1:
            end_index = self._buffer.find(self._thinking_tag_close, start_index)
            if end_index != -1:
                # Yield any text before the thinking block
                if start_index > 0:
                    yield {"type": "text", "content": self._buffer[:start_index]}
                
                thinking_content = self._buffer[start_index + len(self._thinking_tag_open):end_index]
                yield {"type": "thinking", "content": thinking_content.strip()}
                self._buffer = self._buffer[end_index + len(self._thinking_tag_close):]
                start_index = self._buffer.find(self._thinking_tag_open) # Look for next
            else:
                # Incomplete thinking block, wait for more data
                break
        

    def _handle_tool_call_parsing(self) -> Iterator[Dict[str, Any]]:
        """
        Manages the parsing of tool calls from the buffer.
        Detects start and end of tool calls, accumulates content, and yields parsed tool calls.
        """
        # Placeholder for actual tool call detection and parsing logic
        # This will be more complex to handle partial XML/JSON in stream
        
        # Attempt to find a tool call start tag
        if not self._current_tool_name:
            match = self._tool_call_tag_open_regex.search(self._buffer)
            if match:
                # Potential start of a tool call
                # Yield text before the tool call
                if match.start() > 0:
                    yield {"type": "text", "content": self._buffer[:match.start()]}
                
                self._current_tool_name = match.group(1)
                self._tool_call_buffer = self._buffer[match.start():] # Start accumulating from the tag
                self._buffer = "" # Clear main buffer as content moved to tool_call_buffer
                # print(f"DEBUG: Detected tool call start: {self._current_tool_name}, buffer: '{self._tool_call_buffer}'")

        if self._current_tool_name:
            # We are inside a tool call, look for the closing tag
            # Construct the specific closing tag regex for the current tool
            specific_tool_close_regex = re.compile(rf"</{self._current_tool_name}>")
            match_close = specific_tool_close_regex.search(self._tool_call_buffer)
            
            if match_close:
                # Found the closing tag, the tool call is complete
                full_tool_call_str = self._tool_call_buffer[:match_close.end()]
                
                # Placeholder for actual XML/JSON parsing to extract parameters
                # For now, we'll just return the raw string and a dummy parameters dict
                parameters: Dict[str, Any] = {"placeholder_param": "placeholder_value"}
                try:
                    # Basic XML parsing attempt (very naive)
                    # Real implementation would use a proper XML parser library
                    # that can handle streaming/incremental parsing if possible.
                    # For now, just extracting content between tags.
                    # This is a placeholder and will need significant improvement.
                    # Example: <tool_name><param1>value1</param1></tool_name>
                    
                    # This is a very simplified placeholder for parameter extraction
                    # A real implementation would need robust XML/JSON parsing.
                    # For example, using xml.etree.ElementTree or similar.
                    # We are just capturing the whole block for now.
                    pass # Actual parsing logic would go here
                except Exception as e:
                    # Handle parsing errors, maybe yield an error type
                    print(f"Error parsing tool call XML (placeholder): {e}")
                    parameters = {"error": "Failed to parse tool call content"}

                yield {
                    "type": "tool_call",
                    "tool_name": self._current_tool_name,
                    "parameters": parameters, # Replace with actual parsed params
                    "raw_content": full_tool_call_str # For debugging/later parsing
                }
                
                # Reset tool call state and put any remaining buffer content back
                self._buffer = self._tool_call_buffer[match_close.end():]
                self._tool_call_buffer = ""
                self._current_tool_name = None
                # print(f"DEBUG: Parsed tool call. Remaining buffer: '{self._buffer}'")
            # else:
                # print(f"DEBUG: In tool call '{self._current_tool_name}', waiting for closing tag. Buffer: '{self._tool_call_buffer}'")
                # Tool call is not yet complete, keep accumulating in self._tool_call_buffer

    def parse_stream(self, chunk_iterator: Iterator[str]) -> Iterator[Dict[str, Any]]:
        """
        Parses a stream of LLM response chunks.

        Args:
            chunk_iterator: An iterator yielding string chunks from the LLM.

        Yields:
            Dictionaries representing parsed content blocks:
            - {'type': 'text', 'content': '...'}
            - {'type': 'thinking', 'content': '...'}
            - {'type': 'tool_call', 'tool_name': '...', 'parameters': {...}, 'raw_content': '...'}
        """
        for chunk in chunk_iterator:
            self._buffer += chunk
            # print(f"DEBUG: Received chunk. Buffer: '{self._buffer}'")

            # Priority 1: Parse complete thinking blocks
            for item in self._extract_thinking_content():
                yield item
            
            # Priority 2: Parse tool calls (if not in the middle of one already or after thinking)
            # This check ensures we don't try to parse tool calls if we're accumulating for one.
            # Or if the buffer was consumed by thinking block extraction.
            if not self._current_tool_name or self._buffer: # Process buffer if it has content after thinking extraction
                for item in self._handle_tool_call_parsing():
                    yield item
        
        # After all chunks are processed, yield any remaining text in the main buffer
        if self._buffer:
            # If we are still inside a tool call, it means it's incomplete
            if self._current_tool_name:
                # Potentially yield an error or a partial tool call indicator
                # For now, just yielding it as text might be misleading.
                # Or, if the design allows, accumulate and wait for a signal of stream end.
                # This part needs careful design based on how stream termination is handled.
                # print(f"DEBUG: Stream ended with incomplete tool call: {self._tool_call_buffer}")
                # Let's assume for now that incomplete tool calls are an error or should be handled
                # by the caller knowing the stream ended.
                # For this placeholder, we'll just yield the remaining tool_call_buffer content as text
                # if it exists, otherwise the main buffer. This is not ideal.
                if self._tool_call_buffer:
                     yield {"type": "text", "content": self._tool_call_buffer} # Or an error type
                elif self._buffer:
                     yield {"type": "text", "content": self._buffer}

            else: # Not in a tool call, just regular text
                yield {"type": "text", "content": self._buffer}
            self._buffer = "" # Clear buffer

# Example Usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    parser = LLMResponseParser()

    def sample_stream_provider_basic_text():
        yield "This is "
        yield "some basic text."

    def sample_stream_provider_with_thinking():
        yield "Let's think: "
        yield "<thinking>I need to "
        yield "figure this out.</thinking>"
        yield " Okay, done thinking."

    def sample_stream_provider_with_tool_call():
        yield "Okay, I need to use a tool. "
        yield "<my_tool>"
        yield "<param1>value1</param1>"
        yield "<param2>value2</param2>"
        yield "</my_tool>"
        yield " Tool call finished."
        
    def sample_stream_provider_mixed():
        yield "First, some text. "
        yield "<thinking>Pondering deeply...</thinking>"
        yield "Then, a tool: <action_tool><query>what is the weather?</query></action_tool>"
        yield "And finally, more text."

    def sample_stream_provider_interleaved():
        yield "Text part 1. "
        yield "<thinking>Thinking about step 1."
        yield " Still thinking.</thinking>"
        yield " Text part 2, before tool. "
        yield "<my_data_tool><id>123</id>"
        yield "<filter>active</filter></my_data_tool>"
        yield " Text part 3, after tool."
        yield "<thinking>Final thoughts.</thinking>"

    print("--- Basic Text Stream ---")
    for item in parser.parse_stream(sample_stream_provider_basic_text()):
        print(item)
    parser = LLMResponseParser() # Reset parser state

    print("\n--- Thinking Stream ---")
    for item in parser.parse_stream(sample_stream_provider_with_thinking()):
        print(item)
    parser = LLMResponseParser()

    print("\n--- Tool Call Stream ---")
    for item in parser.parse_stream(sample_stream_provider_with_tool_call()):
        print(item)
    parser = LLMResponseParser()
    
    print("\n--- Mixed Stream ---")
    for item in parser.parse_stream(sample_stream_provider_mixed()):
        print(item)
    parser = LLMResponseParser()

    print("\n--- Interleaved Stream ---")
    for item in parser.parse_stream(sample_stream_provider_interleaved()):
        print(item)
    parser = LLMResponseParser()

    def sample_stream_provider_incomplete_tool():
        yield "Using a tool: <incomplete_tool><param>start"
        # Stream ends before tool is closed
        
    print("\n--- Incomplete Tool Call Stream ---")
    for item in parser.parse_stream(sample_stream_provider_incomplete_tool()):
        print(item)
    parser = LLMResponseParser()

    def sample_stream_provider_text_after_incomplete_tool_tag():
        yield "Text <my_tool> then more text"

    print("\n--- Text After Incomplete Tool Tag Stream ---")
    # This scenario highlights the need for robust parsing or clear delimiters.
    # Current naive parsing might misinterpret.
    for item in parser.parse_stream(sample_stream_provider_text_after_incomplete_tool_tag()):
        print(item)
    parser = LLMResponseParser()