"""
Deck Schemas

Pydantic models for deck-related requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CardInDeck(BaseModel):
    """Schema for a card in a deck"""
    card_name: str = Field(..., min_length=1, max_length=100, alias="name")
    quantity: int = Field(..., ge=1, le=100)
    type: Optional[str] = Field(None, max_length=50)  # e.g., "Creature", "Instant"
    mana_cost: Optional[str] = Field(None, max_length=50)  # e.g., "2UU"
    conditions: Optional[str] = None  # e.g., "requires:lands>=2;color=U"
    
    class Config:
        populate_by_name = True  # Allow both 'name' and 'card_name'
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate card quantity"""
        if v < 0:
            raise ValueError('Quantity must be positive')
        return v


class DeckCreate(BaseModel):
    """Schema for creating a deck"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    cards: List[CardInDeck] = Field(..., min_items=1)
    card_count: Optional[str] = Field(None, max_length=10)  # e.g., "60"
    format: Optional[str] = Field(None, max_length=50)  # e.g., "Legacy"
    colors: Optional[List[str]] = None  # e.g., ["U", "G"]
    is_public: bool = False
    tags: Optional[List[str]] = None
    
    @validator('cards')
    def validate_cards(cls, v):
        """Validate deck has cards"""
        if not v:
            raise ValueError('Deck must contain at least one card')
        return v


class DeckUpdate(BaseModel):
    """Schema for updating a deck"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    cards: Optional[List[CardInDeck]] = None
    card_count: Optional[str] = None
    format: Optional[str] = None
    colors: Optional[List[str]] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class DeckResponse(BaseModel):
    """Schema for deck response"""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    cards: List[CardInDeck]
    card_count: Optional[str]
    format: Optional[str]
    colors: Optional[List[str]]
    is_public: bool
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DeckListResponse(BaseModel):
    """Schema for paginated deck list response"""
    total: int
    decks: List[DeckResponse]
    page: int
    page_size: int

