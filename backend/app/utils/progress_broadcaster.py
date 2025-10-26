"""
Progress Broadcaster

Broadcasts simulation progress updates via Redis pub/sub.
This allows Celery workers to send updates that WebSocket clients can receive.
"""

import json
import redis
from typing import Dict, Any
from app.config import settings

# Redis client for broadcasting
redis_client = redis.from_url(settings.REDIS_URL)


def broadcast_progress(simulation_id: str, message: Dict[str, Any]):
    """
    Broadcast a progress update for a simulation via Redis pub/sub.
    
    Args:
        simulation_id: The simulation ID
        message: The message to broadcast (will be JSON serialized)
    """
    channel = f"simulation:{simulation_id}"
    
    try:
        redis_client.publish(channel, json.dumps(message))
    except Exception as e:
        print(f"Error broadcasting progress: {e}")


def broadcast_simulation_status(
    simulation_id: str,
    status: str,
    progress: int = 0,
    message: str = "",
    error: str = None
):
    """
    Broadcast a simulation status update.
    
    Args:
        simulation_id: The simulation ID
        status: Status (PENDING, RUNNING, COMPLETED, FAILED)
        progress: Progress percentage (0-100)
        message: Optional status message
        error: Optional error message
    """
    data = {
        "type": "status",
        "simulation_id": simulation_id,
        "status": status,
        "progress": progress,
        "message": message
    }
    
    if error:
        data["error"] = error
    
    broadcast_progress(simulation_id, data)


def broadcast_simulation_progress(
    simulation_id: str,
    current: int,
    total: int,
    message: str = ""
):
    """
    Broadcast a simulation progress update.
    
    Args:
        simulation_id: The simulation ID
        current: Current progress value
        total: Total value
        message: Optional progress message
    """
    percentage = int((current / total) * 100) if total > 0 else 0
    
    data = {
        "type": "progress",
        "simulation_id": simulation_id,
        "current": current,
        "total": total,
        "progress": percentage,
        "message": message
    }
    
    broadcast_progress(simulation_id, data)


def broadcast_simulation_completed(simulation_id: str):
    """Broadcast that a simulation has completed."""
    broadcast_simulation_status(
        simulation_id=simulation_id,
        status="COMPLETED",
        progress=100,
        message="Simulation completed successfully!"
    )


def broadcast_simulation_error(simulation_id: str, error: str):
    """Broadcast that a simulation has failed."""
    broadcast_simulation_status(
        simulation_id=simulation_id,
        status="FAILED",
        progress=0,
        message="Simulation failed",
        error=error
    )

