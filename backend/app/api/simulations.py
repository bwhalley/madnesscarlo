"""
Simulations API Endpoints

Handles creating and managing simulation runs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.utils.database import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.models.simulation import Simulation, SimulationStatus
from app.models.deck import Deck
from app.models.simulation_config import SimulationConfig
from app.schemas.simulation import (
    SimulationCreate,
    SimulationResponse,
    SimulationListResponse
)
from app.tasks import run_simulation_task


router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.post("/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def create_simulation(
    simulation_data: SimulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new simulation.
    
    This will start a background task to run the simulation.
    """
    # Verify deck exists and belongs to user
    deck = db.query(Deck).filter(
        Deck.id == simulation_data.deck_id,
        Deck.user_id == current_user.id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Get config (use provided config_id or find default)
    config = None
    if simulation_data.config_id:
        # Verify specific config exists and is accessible
        config = db.query(SimulationConfig).filter(
            SimulationConfig.id == simulation_data.config_id,
            (SimulationConfig.user_id == current_user.id) | (SimulationConfig.is_public == True)
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation configuration not found"
            )
    else:
        # No config specified - use default config
        from sqlalchemy import or_
        
        # Try user's default first, then public default
        config = db.query(SimulationConfig).filter(
            SimulationConfig.is_default == True,
            or_(
                SimulationConfig.user_id == current_user.id,
                SimulationConfig.is_public == True
            )
        ).first()
        
        # If no default, just use any public config
        if not config:
            config = db.query(SimulationConfig).filter(
                SimulationConfig.is_public == True
            ).first()
        
        # If still no config, use basic defaults
        if not config:
            # Will use default values from schema
            pass
    
    # Create simulation record
    simulation = Simulation(
        user_id=current_user.id,
        deck_id=simulation_data.deck_id,
        config_id=simulation_data.config_id if simulation_data.config_id else (config.id if config else None),
        runs=simulation_data.runs or (config.default_runs if config else 1000),
        turns=simulation_data.turns or (config.default_turns if config else 4),
        sideboard_plan=simulation_data.sideboard_plan,
        status=SimulationStatus.PENDING
    )
    
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    
    # Start background task
    task = run_simulation_task.delay(
        str(simulation.id),
        str(simulation.deck_id),
        str(simulation.config_id) if simulation.config_id else None
    )
    
    # Store task ID for tracking
    simulation.results = {"task_id": task.id}
    db.commit()
    
    return simulation


@router.get("/", response_model=SimulationListResponse)
def get_simulations(
    skip: int = 0,
    limit: int = 20,
    status_filter: SimulationStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of simulations for the current user."""
    query = db.query(Simulation).filter(Simulation.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Simulation.status == status_filter)
    
    total = query.count()
    simulations = query.order_by(Simulation.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "simulations": simulations,
        "page": (skip // limit) + 1,
        "page_size": limit
    }


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation(
    simulation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific simulation by ID."""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    return simulation


@router.get("/{simulation_id}/status")
def get_simulation_status(
    simulation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current status of a simulation.
    
    This includes progress information if the simulation is running.
    """
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    response = {
        "simulation_id": str(simulation.id),
        "status": simulation.status,
        "progress": simulation.progress,
        "created_at": simulation.created_at,
        "started_at": simulation.started_at,
        "completed_at": simulation.completed_at,
        "error_message": simulation.error_message
    }
    
    # If running, try to get task progress
    if simulation.status == SimulationStatus.RUNNING and simulation.results:
        task_id = simulation.results.get("task_id")
        if task_id:
            from app.celery_app import celery_app
            task = celery_app.AsyncResult(task_id)
            if task.state == "PROGRESS":
                task_info = task.info
                response["progress"] = task_info.get("percentage", 0)
                response["message"] = task_info.get("message", "")
    
    return response


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_simulation(
    simulation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a simulation."""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # If simulation is running, try to cancel it
    if simulation.status == SimulationStatus.RUNNING and simulation.results:
        task_id = simulation.results.get("task_id")
        if task_id:
            from app.celery_app import celery_app
            celery_app.control.revoke(task_id, terminate=True)
    
    db.delete(simulation)
    db.commit()
    
    return None


@router.post("/{simulation_id}/cancel")
def cancel_simulation(
    simulation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a running simulation."""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    if simulation.status != SimulationStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is not running"
        )
    
    # Cancel the Celery task
    if simulation.results:
        task_id = simulation.results.get("task_id")
        if task_id:
            from app.celery_app import celery_app
            celery_app.control.revoke(task_id, terminate=True)
    
    # Update status
    simulation.status = SimulationStatus.CANCELLED
    db.commit()
    
    return {"message": "Simulation cancelled"}


@router.post("/{simulation_id}/export-to-sheets")
def export_simulation_to_sheets(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export simulation results to Google Sheets using user's OAuth tokens.
    
    The spreadsheet will be created in the user's own Google Drive!
    
    Requires:
        - User must be logged in with Google OAuth
        - User must have granted Google Sheets permissions
    
    Returns:
        Dictionary with spreadsheet_id and spreadsheet_url
    """
    from app.services.google_sheets_oauth import get_sheets_oauth_exporter
    from app.services.google_oauth import get_oauth_service
    from datetime import datetime
    
    # Check if user has Google OAuth tokens
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please log in with Google to export to Sheets"
        )
    
    # Check if access token is expired
    oauth_service = get_oauth_service()
    if oauth_service.is_token_expired(current_user.google_token_expires_at):
        # Try to refresh the token
        if current_user.google_refresh_token:
            try:
                refreshed = oauth_service.refresh_access_token(current_user.google_refresh_token)
                current_user.google_access_token = refreshed["access_token"]
                current_user.google_token_expires_at = refreshed["expires_at"]
                db.commit()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Your Google session has expired. Please log in again with Google."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your Google session has expired. Please log in again with Google."
            )
    
    # Get simulation
    simulation = db.query(Simulation).filter(
        Simulation.id == UUID(simulation_id),
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Check if simulation is completed
    if simulation.status != SimulationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation must be completed to export (current status: {simulation.status})"
        )
    
    # Check if results exist
    if not simulation.results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation has no results to export"
        )
    
    # Get deck info
    deck = db.query(Deck).filter(Deck.id == simulation.deck_id).first()
    deck_name = deck.name if deck else "Unknown Deck"
    
    try:
        # Export using user's OAuth token
        exporter = get_sheets_oauth_exporter()
        result = exporter.export_simulation(
            access_token=current_user.google_access_token,
            simulation_data=simulation.results,
            deck_name=deck_name,
            user_email=current_user.email
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Google Sheets: {str(e)}"
        )

