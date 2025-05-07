from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, TEXT, JSON, BigInteger
from sqlalchemy.dialects.postgresql import UUID # For instance_id
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.agent_instance import AgentInstances

class AgentActivityLogs(Base):
    __tablename__ = "agentactivitylogs" # Explicitly defining

    log_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    instance_id = Column(UUID(as_uuid=True), ForeignKey(AgentInstances.instance_id), nullable=False, index=True)
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    log_level = Column(String, nullable=False) # ENUM: 'info', 'debug', 'warning', 'error', 'thought_process'
    message = Column(TEXT, nullable=False)
    details = Column(JSON, nullable=True) # Using JSON for JSONB

    # Relationships (optional)
    # agent_instance = relationship("AgentInstances")