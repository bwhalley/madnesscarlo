"""
Simulation Config Schemas

Pydantic models for simulation configuration.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class BottomPriority(BaseModel):
    """Bottom priority settings for mulligan"""
    prefer_land_at_count: int = Field(default=4, ge=0, le=7)
    protect_key_cards: bool = True


class MulliganStrategy(BaseModel):
    """Mulligan strategy configuration"""
    enabled: bool = True
    min_lands: int = Field(default=2, ge=0, le=7)
    max_lands: int = Field(default=4, ge=0, le=7)
    requires_creature: bool = True
    max_mulligans: int = Field(default=7, ge=0, le=7)
    bottom_priority: Optional[BottomPriority] = None


class IdealSetup(BaseModel):
    """Ideal setup configuration"""
    name: str = Field(..., min_length=1, max_length=100)
    requires_cards: List[str] = Field(default_factory=list)
    requires_in_play: Optional[List[str]] = Field(default_factory=list)
    requires_colors: Optional[List[str]] = Field(default_factory=list)
    requires_in_graveyard: Optional[List[str]] = Field(default_factory=list)
    requires_min_lands: Optional[int] = Field(default=0, ge=0)
    requires_any_creature_in_hand: Optional[bool] = False
    turn_limit: int = Field(default=4, ge=1, le=20)


class SideboardPlan(BaseModel):
    """Sideboard plan configuration"""
    name: str
    board_in: Dict[str, int] = Field(default_factory=dict)  # {"Counterspell": 2}
    board_out: Dict[str, int] = Field(default_factory=dict)  # {"Naturalize": 2}


class SimulationConfigCreate(BaseModel):
    """Schema for creating a simulation config"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    default_runs: int = Field(default=1000, ge=100, le=100000)
    default_turns: int = Field(default=4, ge=1, le=20)
    key_card_turn_limit: int = Field(default=4, ge=1, le=20)
    key_cards: Optional[List[str]] = Field(default_factory=list)
    mulligan_strategy: MulliganStrategy = Field(default_factory=MulliganStrategy)
    ideal_setups: Optional[List[IdealSetup]] = Field(default_factory=list)
    sideboard_plans: Optional[Dict[str, SideboardPlan]] = Field(default_factory=dict)
    is_default: bool = False
    is_public: bool = False


class SimulationConfigUpdate(BaseModel):
    """Schema for updating a simulation config"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    default_runs: Optional[int] = Field(None, ge=100, le=100000)
    default_turns: Optional[int] = Field(None, ge=1, le=20)
    key_card_turn_limit: Optional[int] = Field(None, ge=1, le=20)
    key_cards: Optional[List[str]] = None
    mulligan_strategy: Optional[MulliganStrategy] = None
    ideal_setups: Optional[List[IdealSetup]] = None
    sideboard_plans: Optional[Dict[str, SideboardPlan]] = None
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None


class SimulationConfigResponse(BaseModel):
    """Schema for simulation config response"""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    default_runs: int
    default_turns: int
    key_card_turn_limit: int
    key_cards: Optional[List[str]]
    mulligan_strategy: Dict[str, Any]  # JSONB from database
    ideal_setups: Optional[List[Dict[str, Any]]]
    sideboard_plans: Optional[Dict[str, Any]]
    is_default: bool
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

