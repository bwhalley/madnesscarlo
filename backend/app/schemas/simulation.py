"""
Simulation Schemas

Pydantic models for simulation runs.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class SimulationCreate(BaseModel):
    """Schema for starting a new simulation"""
    deck_id: UUID
    config_id: Optional[UUID] = None  # If None, use default config
    runs: int = Field(default=1000, ge=100, le=100000)
    turns: int = Field(default=4, ge=1, le=20)
    sideboard_plan: Optional[str] = None  # e.g., "vs_combo"


class SimulationResponse(BaseModel):
    """Schema for simulation response"""
    id: UUID
    user_id: UUID
    deck_id: Optional[UUID]
    config_id: Optional[UUID]
    runs: int
    turns: int
    sideboard_plan: Optional[str]
    status: str  # pending, running, completed, failed, cancelled
    progress: int  # 0-100
    results: Optional[Dict[str, Any]]  # Full simulation results
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SimulationListResponse(BaseModel):
    """Schema for paginated simulation list"""
    total: int
    simulations: list[SimulationResponse]
    page: int
    page_size: int

