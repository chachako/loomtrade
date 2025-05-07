from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, DECIMAL, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base
from app.models.agent_instance import AgentInstances

class Positions(Base):
    __tablename__ = "positions" # Explicitly defining

    position_id_internal = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    instance_id = Column(UUID(as_uuid=True), ForeignKey(AgentInstances.instance_id), nullable=False, index=True)
    exchange_position_id = Column(String, nullable=True, index=True) # Can be null if not provided by exchange or for internal tracking
    
    pair = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False) # ENUM: 'long', 'short'
    entry_price = Column(DECIMAL, nullable=False)
    quantity = Column(DECIMAL, nullable=False)
    current_mark_price = Column(DECIMAL, nullable=True)
    unrealized_pnl = Column(DECIMAL, nullable=True)
    leverage = Column(Integer, nullable=False) # Assuming leverage is an integer
    initial_margin = Column(DECIMAL, nullable=True)
    liquidation_price = Column(DECIMAL, nullable=True)
    stop_loss_price_agent = Column(DECIMAL, nullable=True)
    take_profit_price_agent = Column(DECIMAL, nullable=True)
    opened_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    strategy_snapshot = Column(JSON, nullable=True) # Using JSON for JSONB

    # Relationships (optional)
    # agent_instance = relationship("AgentInstances")
    # trade_orders = relationship("TradeOrders", back_populates="position") # If TradeOrders has a 'position' relationship