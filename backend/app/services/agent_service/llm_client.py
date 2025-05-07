# backend/app/services/agent_service/llm_client.py
import httpx
import asyncio
from typing import AsyncGenerator, Dict, List, Optional, Any

# 确保已安装 httpx: pip install httpx[http2]
# from app.models.llm_provider_config import LLMProviderConfig # 假设的配置模型路径

# 临时的 LLMProviderConfig 占位符，实际应从数据库加载
class LLMProviderConfig:
    def __init__(self, provider_name: str, model_name: str, api_key: str, base_url: Optional[str] = None):
        self.provider_name = provider_name
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

class LLMClient:
    """
    Handles interactions with various LLM providers.
    """
    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=60.0) # 增加超时时间

    async def _call_openai_api(
        self, messages: List[Dict[str, str]], temperature: float, max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """
        Placeholder for OpenAI API call logic.
        Yields completion chunks.
        """
        # 实际的 API 调用逻辑会在这里
        # 例如:
        # api_url = self.config.base_url or "https://api.openai.com/v1/chat/completions"
        # headers = {
        #     "Authorization": f"Bearer {self.config.api_key}",
        #     "Content-Type": "application/json",
        # }
        # payload = {
        #     "model": self.config.model_name,
        #     "messages": messages,
        #     "temperature": temperature,
        #     "max_tokens": max_tokens,
        #     "stream": True,
        # }
        # async with self.http_client.stream("POST", api_url, json=payload, headers=headers) as response:
        #     response.raise_for_status() # Will raise an exception for 4XX/5XX responses
        #     async for chunk in response.aiter_text():
        #         # Process chunk (e.g., parse Server-Sent Events)
        #         yield chunk
        print(f"Calling OpenAI API (placeholder) with model: {self.config.model_name}")
        await asyncio.sleep(0.1) # Simulate async operation
        for i in range(5):
            yield f"OpenAI chunk {i+1} for messages: {messages[0]['content'][:20]}... "
            await asyncio.sleep(0.05)

    async def _call_anthropic_api(
        self, messages: List[Dict[str, str]], temperature: float, max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """
        Placeholder for Anthropic API call logic.
        Yields completion chunks.
        """
        # 实际的 API 调用逻辑会在这里
        print(f"Calling Anthropic API (placeholder) with model: {self.config.model_name}")
        await asyncio.sleep(0.1) # Simulate async operation
        for i in range(3):
            yield f"Anthropic chunk {i+1} for messages: {messages[0]['content'][:20]}... "
            await asyncio.sleep(0.05)

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Core method to get streaming completions from the configured LLM provider.

        Args:
            messages: A list of message dictionaries (e.g., [{"role": "user", "content": "Hello"}]).
            temperature: The sampling temperature.
            max_tokens: The maximum number of tokens to generate.

        Yields:
            Streamed response chunks (strings).
        """
        try:
            if self.config.provider_name.lower() == "openai":
                async for chunk in self._call_openai_api(messages, temperature, max_tokens):
                    yield chunk
            elif self.config.provider_name.lower() == "anthropic":
                async for chunk in self._call_anthropic_api(messages, temperature, max_tokens):
                    yield chunk
            # Add other providers here
            else:
                error_message = f"Unsupported LLM provider: {self.config.provider_name}"
                print(error_message) # Or log this
                yield f"Error: {error_message}" # Yield an error message if streaming
                # raise ValueError(error_message) # Or raise an exception if not streaming

        except httpx.HTTPStatusError as e:
            # Handle HTTP errors (e.g., 4XX, 5XX responses)
            error_message = f"API Error: {e.response.status_code} - {e.response.text}"
            print(f"HTTPStatusError: {error_message}")
            yield f"Error: {error_message}"
        except httpx.RequestError as e:
            # Handle network errors (e.g., connection issues)
            error_message = f"Network Error: {str(e)}"
            print(f"RequestError: {error_message}")
            yield f"Error: {error_message}"
        except Exception as e:
            # Handle other unexpected errors
            error_message = f"An unexpected error occurred: {str(e)}"
            print(f"Unexpected error: {error_message}")
            yield f"Error: {error_message}"
        finally:
            # Consider if client needs to be closed here or managed externally
            # For a long-running service, you might keep the client open.
            # await self.close() # If you want to close after each call (less efficient)
            pass

    async def close(self):
        """
        Closes the underlying HTTP client.
        """
        await self.http_client.aclose()

# Example Usage (for testing purposes, can be removed or kept under if __name__ == "__main__"):
async def main():
    # Example: OpenAI
    openai_config = LLMProviderConfig(
        provider_name="OpenAI",
        model_name="gpt-4-turbo",
        api_key="YOUR_OPENAI_API_KEY", # Replace with actual key for testing
        base_url="https://api.openai.com/v1" # Optional, often not needed for OpenAI
    )
    openai_client = LLMClient(config=openai_config)

    print("\n--- Testing OpenAI Client ---")
    messages_openai = [{"role": "user", "content": "Hello OpenAI, tell me a joke."}]
    try:
        async for chunk in openai_client.stream_completion(messages_openai, temperature=0.5, max_tokens=50):
            print(chunk, end="", flush=True)
        print("\nOpenAI stream finished.")
    except Exception as e:
        print(f"\nError during OpenAI test: {e}")
    finally:
        await openai_client.close()


    # Example: Anthropic
    anthropic_config = LLMProviderConfig(
        provider_name="Anthropic",
        model_name="claude-3-opus-20240229",
        api_key="YOUR_ANTHROPIC_API_KEY" # Replace with actual key for testing
    )
    anthropic_client = LLMClient(config=anthropic_config)

    print("\n\n--- Testing Anthropic Client ---")
    messages_anthropic = [{"role": "user", "content": "Hello Anthropic, what is the capital of France?"}]
    try:
        async for chunk in anthropic_client.stream_completion(messages_anthropic, temperature=0.5, max_tokens=50):
            print(chunk, end="", flush=True)
        print("\nAnthropic stream finished.")
    except Exception as e:
        print(f"\nError during Anthropic test: {e}")
    finally:
        await anthropic_client.close()

    # Example: Unsupported Provider
    unsupported_config = LLMProviderConfig(
        provider_name="ImaginaryLLM",
        model_name="model-x",
        api_key="KEY"
    )
    unsupported_client = LLMClient(config=unsupported_config)
    print("\n\n--- Testing Unsupported Provider ---")
    messages_unsupported = [{"role": "user", "content": "Hello?"}]
    try:
        async for chunk in unsupported_client.stream_completion(messages_unsupported):
            print(chunk, end="", flush=True)
        print("\nUnsupported stream finished (expected error message).")
    except Exception as e:
        print(f"\nError during unsupported test: {e}")
    finally:
        await unsupported_client.close()


if __name__ == "__main__":
    # To run this example:
    # 1. Make sure you have httpx installed: pip install httpx[http2] asyncio
    # 2. Save this file as llm_client.py
    # 3. Run from your terminal: python llm_client.py
    # Note: You'll need to replace "YOUR_OPENAI_API_KEY" and "YOUR_ANTHROPIC_API_KEY"
    # with actual keys if you want the placeholder API calls to be replaced with real ones.
    # For now, it will just print placeholder messages.
    asyncio.run(main())