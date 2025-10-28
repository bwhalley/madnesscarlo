"""
Simulation Configs API

CRUD operations for simulation configurations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.utils.database import get_db
from app.utils.security import get_current_user_id
from app.schemas.simulation_config import (
    SimulationConfigCreate,
    SimulationConfigUpdate,
    SimulationConfigResponse
)
from app.models.simulation_config import SimulationConfig

router = APIRouter(prefix="/api/configs", tags=["simulation-configs"])


@router.get("/", response_model=List[SimulationConfigResponse])
def list_configs(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all simulation configs for the current user, plus public configs.
    """
    from sqlalchemy import or_
    
    configs = db.query(SimulationConfig).filter(
        or_(
            SimulationConfig.user_id == user_id,
            SimulationConfig.is_public == True
        )
    ).order_by(
        SimulationConfig.is_default.desc(),  # Default configs first
        SimulationConfig.updated_at.desc()
    ).all()
    
    return [SimulationConfigResponse.from_orm(config) for config in configs]


@router.get("/default", response_model=SimulationConfigResponse)
def get_default_config(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get the default simulation config.
    
    Priority:
    1. User's own default config
    2. Public default config
    3. Most recent user config
    4. Most recent public config
    """
    from sqlalchemy import or_
    
    # Try to find user's default config
    config = db.query(SimulationConfig).filter(
        SimulationConfig.user_id == user_id,
        SimulationConfig.is_default == True
    ).first()
    
    # Try to find public default config
    if not config:
        config = db.query(SimulationConfig).filter(
            SimulationConfig.is_public == True,
            SimulationConfig.is_default == True
        ).first()
    
    # If no default, get most recent (user or public)
    if not config:
        config = db.query(SimulationConfig).filter(
            or_(
                SimulationConfig.user_id == user_id,
                SimulationConfig.is_public == True
            )
        ).order_by(SimulationConfig.updated_at.desc()).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No simulation configs found"
        )
    
    return SimulationConfigResponse.from_orm(config)


@router.post("/", response_model=SimulationConfigResponse, status_code=status.HTTP_201_CREATED)
def create_config(
    config_data: SimulationConfigCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new simulation config.
    """
    # If this is being set as default, unset other defaults
    if config_data.is_default:
        db.query(SimulationConfig).filter(
            SimulationConfig.user_id == user_id,
            SimulationConfig.is_default == True
        ).update({"is_default": False})
    
    # Convert Pydantic models to dicts for JSONB storage
    mulligan_dict = config_data.mulligan_strategy.dict()
    ideal_setups_dict = [setup.dict() for setup in config_data.ideal_setups] if config_data.ideal_setups else []
    sideboard_plans_dict = {}
    if config_data.sideboard_plans:
        sideboard_plans_dict = {
            key: plan.dict() for key, plan in config_data.sideboard_plans.items()
        }
    
    # Create config
    new_config = SimulationConfig(
        user_id=user_id,
        name=config_data.name,
        description=config_data.description,
        default_runs=config_data.default_runs,
        default_turns=config_data.default_turns,
        key_card_turn_limit=config_data.key_card_turn_limit,
        key_cards=config_data.key_cards,
        mulligan_strategy=mulligan_dict,
        ideal_setups=ideal_setups_dict,
        sideboard_plans=sideboard_plans_dict,
        is_default=config_data.is_default,
        is_public=config_data.is_public
    )
    
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    return SimulationConfigResponse.from_orm(new_config)


@router.get("/{config_id}", response_model=SimulationConfigResponse)
def get_config(
    config_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific simulation config by ID.
    """
    config = db.query(SimulationConfig).filter(
        SimulationConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    # Check access permissions
    if str(config.user_id) != user_id and not config.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return SimulationConfigResponse.from_orm(config)


@router.put("/{config_id}", response_model=SimulationConfigResponse)
def update_config(
    config_id: UUID,
    config_data: SimulationConfigUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a simulation config.
    """
    config = db.query(SimulationConfig).filter(
        SimulationConfig.id == config_id,
        SimulationConfig.user_id == user_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    # If setting as default, unset other defaults
    if config_data.is_default:
        db.query(SimulationConfig).filter(
            SimulationConfig.user_id == user_id,
            SimulationConfig.id != config_id,
            SimulationConfig.is_default == True
        ).update({"is_default": False})
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    
    # Convert Pydantic models to dicts for JSONB storage
    if "mulligan_strategy" in update_data and update_data["mulligan_strategy"] is not None:
        update_data["mulligan_strategy"] = config_data.mulligan_strategy.dict()
    
    if "ideal_setups" in update_data and update_data["ideal_setups"] is not None:
        update_data["ideal_setups"] = [setup.dict() for setup in config_data.ideal_setups]
    
    if "sideboard_plans" in update_data and update_data["sideboard_plans"] is not None:
        update_data["sideboard_plans"] = {
            key: plan.dict() for key, plan in config_data.sideboard_plans.items()
        }
    
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return SimulationConfigResponse.from_orm(config)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    config_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a simulation config.
    """
    config = db.query(SimulationConfig).filter(
        SimulationConfig.id == config_id,
        SimulationConfig.user_id == user_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    db.delete(config)
    db.commit()
    
    return None


@router.post("/{config_id}/duplicate", response_model=SimulationConfigResponse, status_code=status.HTTP_201_CREATED)
def duplicate_config(
    config_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Duplicate an existing config (your own or public).
    Creates a new config with the same settings but different name.
    """
    # Find the config (must be user's own or public)
    from sqlalchemy import or_
    
    original_config = db.query(SimulationConfig).filter(
        SimulationConfig.id == config_id,
        or_(
            SimulationConfig.user_id == user_id,
            SimulationConfig.is_public == True
        )
    ).first()
    
    if not original_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found or not accessible"
        )
    
    # Create a new config with the same settings
    new_config = SimulationConfig(
        user_id=user_id,
        name=f"{original_config.name} (Copy)",
        description=original_config.description,
        default_runs=original_config.default_runs,
        default_turns=original_config.default_turns,
        key_card_turn_limit=original_config.key_card_turn_limit,
        key_cards=original_config.key_cards,
        mulligan_strategy=original_config.mulligan_strategy,
        ideal_setups=original_config.ideal_setups,
        sideboard_plans=original_config.sideboard_plans,
        is_default=False,  # Don't make duplicates default
        is_public=False    # Don't make duplicates public
    )
    
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    return SimulationConfigResponse.from_orm(new_config)


@router.post("/{config_id}/set-default", response_model=SimulationConfigResponse)
def set_default_config(
    config_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Set a config as the default for the user.
    """
    config = db.query(SimulationConfig).filter(
        SimulationConfig.id == config_id,
        SimulationConfig.user_id == user_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    # Unset all other defaults
    db.query(SimulationConfig).filter(
        SimulationConfig.user_id == user_id,
        SimulationConfig.id != config_id,
        SimulationConfig.is_default == True
    ).update({"is_default": False})
    
    # Set this as default
    config.is_default = True
    db.commit()
    db.refresh(config)
    
    return SimulationConfigResponse.from_orm(config)

