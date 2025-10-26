"""
Deck Model

Stores MTG deck lists with card information.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.utils.database import Base


class Deck(Base):
    """Deck list model"""
    __tablename__ = "decks"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Owner
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Deck info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Cards as JSON array
    # Format: [{"card_name": "Island", "quantity": 9, "type": "Land", "mana_cost": "", "conditions": "effect:mana_U;category:land"}]
    cards = Column(JSONB, nullable=False)
    
    # Metadata
    card_count = Column(String(10), nullable=True)  # e.g., "60", "100", "variable"
    format = Column(String(50), nullable=True)  # e.g., "Legacy", "Modern", "Commander"
    colors = Column(JSONB, nullable=True)  # Array of colors: ["U", "G"]
    
    # Sharing
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Tags for organization
    tags = Column(JSONB, nullable=True)  # Array of strings: ["combo", "control"]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Deck {self.name} ({len(self.cards) if self.cards else 0} cards)>"

