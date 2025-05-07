from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.sql import func
# from sqlalchemy.dialects.postgresql import UUID # Not using UUID for llm_config_id
# import uuid # Not using UUID

from app.db.base_class import Base
from app.models.user import Users # For ForeignKey

class LLMProviderConfigs(Base):
    __tablename__ = "llmproviderconfigs" # Explicitly defining to match specs

    llm_config_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(Users.user_id), nullable=False, index=True)
    provider_name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    # api_key will be encrypted in application logic, stored as String
    api_key = Column(String, nullable=False) # Placeholder for encrypted value
    base_url = Column(String, nullable=True) # For custom LLM API endpoints
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relationship (optional)
    # user = relationship("Users")