from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base
from app.models.user import Users
# Need to import other models for ForeignKeys once they are created
# from app.models.trader_profile import TraderProfiles # Placeholder
# from app.models.trading_strategy import TradingStrategies # Placeholder
from app.models.exchange_config import ExchangeAPIKeys
from app.models.llm_provider_config import LLMProviderConfigs


class AgentInstances(Base):
    __tablename__ = "agentinstances" # Explicitly defining

    instance_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey(Users.user_id), nullable=False, index=True)
    
    # These foreign keys will point to tables created later.
    # For now, define them as Integer or UUID based on their eventual PK type.
    # Assuming TraderProfiles and TradingStrategies will have Integer PKs for now.
    active_profile_id = Column(Integer, 
                               # ForeignKey("traderprofiles.profile_id"), # Define when TraderProfiles exists
                               nullable=False, index=True)
    active_strategy_id = Column(Integer, 
                                # ForeignKey("tradingstrategies.strategy_id"), # Define when TradingStrategies exists
                                nullable=False, index=True)
    
    active_exchange_api_key_id = Column(Integer, ForeignKey(ExchangeAPIKeys.api_key_id), nullable=False, index=True)
    active_llm_config_id = Column(Integer, ForeignKey(LLMProviderConfigs.llm_config_id), nullable=False, index=True)
    
    status = Column(String, nullable=False) # ENUM: 'running', 'paused', 'stopped', 'error'
    current_short_term_memory = Column(JSON, nullable=True) # Using JSON for JSONB
    last_heartbeat_at = Column(TIMESTAMP, nullable=True)
    started_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    stopped_at = Column(TIMESTAMP, nullable=True)

    # Relationships (optional)
    # user = relationship("Users")
    # exchange_api_key = relationship("ExchangeAPIKeys")
    # llm_config = relationship("LLMProviderConfigs")
    # trader_profile = relationship("TraderProfiles")
    # trading_strategy = relationship("TradingStrategies")