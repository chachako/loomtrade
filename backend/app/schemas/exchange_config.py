from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ExchangeConfigBase(BaseModel):
    exchange_name: str = Field(..., description="Name of the exchange (e.g., Binance, Coinbase)")
    market_type: str = Field(..., description="Type of market (e.g., crypto, stock, forex)")
    permissions: Optional[str] = Field(None, description="API key permissions (e.g., read_info,trade)")
    is_active: bool = Field(True, description="Is this configuration active?")

class ExchangeConfigCreate(ExchangeConfigBase):
    api_key: str = Field(..., description="API Key for the exchange")
    secret_key: str = Field(..., description="Secret Key for the exchange")
    passphrase: Optional[str] = Field(None, description="Passphrase for the exchange (if required)")

class ExchangeConfigUpdate(BaseModel):
    exchange_name: Optional[str] = Field(None, description="Name of the exchange")
    market_type: Optional[str] = Field(None, description="Type of market")
    api_key: Optional[str] = Field(None, description="New API Key for the exchange (if updating)")
    secret_key: Optional[str] = Field(None, description="New Secret Key for the exchange (if updating)")
    passphrase: Optional[str] = Field(None, description="New Passphrase for the exchange (if updating or clearing)")
    permissions: Optional[str] = Field(None, description="API key permissions")
    is_active: Optional[bool] = Field(None, description="Is this configuration active?")

class ExchangeConfig(ExchangeConfigBase):
    api_key_id: int = Field(..., description="Unique ID of the API key configuration")
    user_id: int = Field(..., description="ID of the user who owns this configuration")
    api_key_set: bool = Field(..., description="Indicates if the API key is set")
    secret_key_set: bool = Field(..., description="Indicates if the Secret key is set")
    passphrase_set: bool = Field(..., description="Indicates if the Passphrase is set (relevant if exchange requires it)")
    created_at: datetime = Field(..., description="Timestamp of creation")
    last_tested_at: Optional[datetime] = Field(None, description="Timestamp of last successful test")

    class Config:
        orm_mode = True # Pydantic V1
        # from_attributes = True # Pydantic V2