from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, TEXT, DECIMAL, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base
from app.models.agent_instance import AgentInstances
from app.models.position import Positions # For ForeignKey, define when Positions exists

class TradeOrders(Base):
    __tablename__ = "tradeorders" # Explicitly defining

    order_id_internal = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    instance_id = Column(UUID(as_uuid=True), ForeignKey(AgentInstances.instance_id), nullable=False, index=True)
    
    position_id_internal = Column(UUID(as_uuid=True),
                                  ForeignKey(Positions.position_id_internal), # Define when Positions exists
                                  nullable=True, index=True)
    
    exchange_order_id = Column(String, nullable=False, index=True)
    pair = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False) # ENUM: 'buy', 'sell'
    type = Column(String, nullable=False) # ENUM: 'market', 'limit', etc.
    status = Column(String, nullable=False, index=True) # ENUM: 'new', 'partially_filled', 'filled', 'canceled', 'rejected', 'expired'
    price = Column(DECIMAL, nullable=True) # For limit orders
    quantity_ordered = Column(DECIMAL, nullable=False)
    quantity_filled = Column(DECIMAL, nullable=True, default=0)
    average_fill_price = Column(DECIMAL, nullable=True)
    fee_amount = Column(DECIMAL, nullable=True)
    fee_currency = Column(String, nullable=True)
    created_at_agent = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at_exchange = Column(TIMESTAMP, nullable=True)
    reason = Column(TEXT, nullable=True) # e.g., "Entry signal from Strategy X"

    # Relationships (optional)
    # agent_instance = relationship("AgentInstances")
    # position = relationship("Positions")