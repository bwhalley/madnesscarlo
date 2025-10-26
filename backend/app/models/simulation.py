"""
Simulation Model

Stores simulation runs and their results.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from app.utils.database import Base


class SimulationStatus(str, enum.Enum):
    """Simulation execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Simulation(Base):
    """Simulation run model"""
    __tablename__ = "simulations"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Owner
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # References
    deck_id = Column(UUID(as_uuid=True), ForeignKey("decks.id", ondelete="SET NULL"), nullable=True, index=True)
    config_id = Column(UUID(as_uuid=True), ForeignKey("simulation_configs.id", ondelete="SET NULL"), nullable=True)
    
    # Simulation parameters
    runs = Column(Integer, nullable=False)
    turns = Column(Integer, nullable=False)
    
    # Sideboard info (if applicable)
    sideboard_plan = Column(String(100), nullable=True)  # e.g., "vs_combo"
    
    # Execution
    status = Column(SQLEnum(SimulationStatus), default=SimulationStatus.PENDING, nullable=False, index=True)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Results stored as JSON
    # Contains all the statistics: card_stats, key_card_stats, ideal_setups, mulligan_stats, etc.
    results = Column(JSONB, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Simulation {self.id} ({self.status})>"

