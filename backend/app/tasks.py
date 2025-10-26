"""
Celery Tasks

Background tasks for running simulations.
"""

from datetime import datetime
from typing import Dict, Any
from uuid import UUID

from app.celery_app import celery_app
from app.utils.database import SessionLocal
from app.models.simulation import Simulation, SimulationStatus
from app.models.deck import Deck
from app.models.simulation_config import SimulationConfig
from app.simulation.runner import run_simulations
from app.utils.progress_broadcaster import (
    broadcast_simulation_status,
    broadcast_simulation_progress,
    broadcast_simulation_completed,
    broadcast_simulation_error
)


@celery_app.task(bind=True, name="app.tasks.run_simulation_task")
def run_simulation_task(
    self,
    simulation_id: str,
    deck_id: str,
    config_id: str
) -> Dict[str, Any]:
    """
    Run a Monte Carlo simulation as a background task.
    
    Args:
        simulation_id: UUID of the simulation record
        deck_id: UUID of the deck to simulate
        config_id: UUID of the simulation configuration
        
    Returns:
        Dictionary with simulation results
    """
    db = SessionLocal()
    
    try:
        # Load simulation record
        simulation = db.query(Simulation).filter(
            Simulation.id == UUID(simulation_id)
        ).first()
        
        if not simulation:
            return {"error": "Simulation not found"}
        
        # Update status to running
        simulation.status = SimulationStatus.RUNNING
        simulation.started_at = datetime.utcnow()
        db.commit()
        
        # Broadcast that simulation has started
        broadcast_simulation_status(
            simulation_id=simulation_id,
            status="RUNNING",
            progress=0,
            message="Simulation started..."
        )
        
        # Load deck
        deck = db.query(Deck).filter(Deck.id == UUID(deck_id)).first()
        if not deck:
            simulation.status = SimulationStatus.FAILED
            simulation.results = {"error": "Deck not found"}
            db.commit()
            return {"error": "Deck not found"}
        
        # Load config
        config = db.query(SimulationConfig).filter(
            SimulationConfig.id == UUID(config_id)
        ).first()
        if not config:
            simulation.status = SimulationStatus.FAILED
            simulation.results = {"error": "Configuration not found"}
            db.commit()
            return {"error": "Configuration not found"}
        
        # Prepare card data for simulation
        cards_data = []
        # deck.cards is a JSONB field containing the list of cards
        cards_list = deck.cards if isinstance(deck.cards, list) else []
        for card in cards_list:
            cards_data.append({
                "name": card.get("name") or card.get("card_name"),
                "quantity": card.get("quantity", 1),
                "type": card.get("type", ""),
                "mana_cost": card.get("mana_cost", ""),
                "conditions": card.get("conditions", "")
            })
        
        # Prepare simulation config
        sim_config = {
            "key_cards": config.key_cards or [],
            "key_card_turn_limit": config.key_card_turn_limit or 4,
            "ideal_setups": config.ideal_setups or [],
            "mulligan_strategy": config.mulligan_strategy or {}
        }
        
        # Get number of runs
        runs = config.default_runs or 1000
        turns = config.default_turns or 4
        
        # Progress callback
        def progress_callback(current: int, total: int, message: str):
            """Update task progress."""
            # Update Celery task state
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": current,
                    "total": total,
                    "message": message,
                    "percentage": int((current / total) * 100) if total > 0 else 0
                }
            )
            
            # Broadcast via WebSocket
            broadcast_simulation_progress(
                simulation_id=simulation_id,
                current=current,
                total=total,
                message=message
            )
        
        # Run simulation
        results = run_simulations(
            cards_data=cards_data,
            runs=runs,
            turns=turns,
            config=sim_config,
            progress_callback=progress_callback
        )
        
        # Save results
        simulation.results = results
        simulation.status = SimulationStatus.COMPLETED
        simulation.completed_at = datetime.utcnow()
        db.commit()
        
        # Broadcast completion
        broadcast_simulation_completed(simulation_id)
        
        return {
            "simulation_id": str(simulation_id),
            "status": "completed",
            "results": results
        }
        
    except Exception as e:
        # Mark simulation as failed
        if simulation:
            simulation.status = SimulationStatus.FAILED
            simulation.results = {"error": str(e)}
            simulation.completed_at = datetime.utcnow()
            db.commit()
        
        # Broadcast error
        broadcast_simulation_error(simulation_id, str(e))
        
        raise e
        
    finally:
        db.close()

