from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, TEXT
from sqlalchemy.sql import func
# from sqlalchemy.dialects.postgresql import UUID # Not using UUID for api_key_id
# import uuid # Not using UUID

from app.db.base_class import Base
from app.models.user import Users # For ForeignKey

class ExchangeAPIKeys(Base):
    __tablename__ = "exchangeapikeys" # Explicitly defining to match specs for 'ExchangeAPIKeys'

    api_key_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(Users.user_id), nullable=False, index=True)
    exchange_name = Column(String, nullable=False)
    # api_key, secret_key, passphrase will be encrypted in application logic, stored as String
    api_key = Column(String, nullable=False) # Placeholder for encrypted value
    secret_key = Column(String, nullable=False) # Placeholder for encrypted value
    passphrase = Column(String, nullable=True) # Placeholder for encrypted value
    permissions = Column(TEXT, nullable=True) # e.g., "read_info,trade"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    last_tested_at = Column(TIMESTAMP, nullable=True)

    # Relationship (optional, can be added later if needed for ORM queries)
    # user = relationship("Users")