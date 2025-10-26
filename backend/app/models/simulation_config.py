"""
Simulation Configuration Model

Stores simulation parameters and strategies.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.utils.database import Base


class SimulationConfig(Base):
    """Simulation configuration model"""
    __tablename__ = "simulation_configs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Owner
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Config info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Simulation parameters
    default_runs = Column(Integer, default=1000, nullable=False)
    default_turns = Column(Integer, default=4, nullable=False)
    key_card_turn_limit = Column(Integer, default=4, nullable=False)
    
    # Key cards to track
    key_cards = Column(JSONB, nullable=True)  # Array of card names: ["Survival of the Fittest", ...]
    
    # Mulligan strategy
    # Format: {"enabled": true, "min_lands": 2, "max_lands": 4, "requires_creature": true, ...}
    mulligan_strategy = Column(JSONB, nullable=False, default=dict)
    
    # Ideal setups to track
    # Format: [{"name": "Survival Engine", "requires_cards": [...], "requires_colors": [...], ...}]
    ideal_setups = Column(JSONB, nullable=True, default=list)
    
    # Sideboard plans
    # Format: {"vs_combo": {"name": "Vs Combo", "board_in": {...}, "board_out": {...}}}
    sideboard_plans = Column(JSONB, nullable=True, default=dict)
    
    # Metadata
    is_default = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SimulationConfig {self.name}>"

