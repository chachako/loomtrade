from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.sql import func
# from sqlalchemy.dialects.postgresql import UUID # Not using UUID for user_id as per decision
# import uuid # Not using UUID for user_id

from app.db.base_class import Base

class Users(Base):
    __tablename__ = "users"  # Explicitly defining to match specs, though Base would generate it

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    # is_active = Column(Boolean, default=True) # Not in specs, but common. Will omit for now.