from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Annotated
from datetime import datetime

class LLMProviderConfigBase(BaseModel):
    provider_name: Annotated[str, Field(..., description="The name of the LLM provider (e.g., OpenAI, Anthropic, Google).")]
    model_name: Annotated[str, Field(..., description="The specific model name (e.g., gpt-4, claude-3-opus-20240229, gemini-pro).")]
    base_url: Optional[Annotated[HttpUrl, Field(description="Optional base URL for custom LLM API endpoints.")]] = None
    is_active: Annotated[bool, Field(default=True, description="Whether this configuration is active.")]

class LLMProviderConfigCreate(LLMProviderConfigBase):
    api_key: Annotated[str, Field(..., description="The API key for the LLM provider. This will be encrypted before storage.")]

class LLMProviderConfigUpdate(BaseModel):
    provider_name: Optional[Annotated[str, Field(description="The name of the LLM provider.")]] = None
    model_name: Optional[Annotated[str, Field(description="The specific model name.")]] = None
    api_key: Optional[Annotated[str, Field(description="The new API key for the LLM provider. If provided, it will be encrypted.")]] = None
    base_url: Optional[Annotated[HttpUrl, Field(description="Optional base URL for custom LLM API endpoints.")]] = None
    is_active: Optional[Annotated[bool, Field(description="Whether this configuration is active.")]] = None

class LLMProviderConfig(LLMProviderConfigBase):
    llm_config_id: Annotated[int, Field(description="The unique identifier for the LLM provider configuration.")]
    user_id: Annotated[int, Field(description="The ID of the user who owns this configuration.")]
    api_key_set: Annotated[bool, Field(description="Indicates whether an API key has been set for this configuration.")]
    created_at: Annotated[datetime, Field(description="The timestamp when the configuration was created.")]

    class Config:
        orm_mode = True # Pydantic V1 style for compatibility, consider `from_attributes = True` for V2
        # For Pydantic V2, use:
        # model_config = {"from_attributes": True}