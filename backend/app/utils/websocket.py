"""
WebSocket Manager for Real-Time Simulation Updates

Manages WebSocket connections and broadcasts simulation progress updates.
"""

from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    
    Connections are organized by simulation_id so we can broadcast
    updates to specific simulations.
    """
    
    def __init__(self):
        # Dict of simulation_id -> set of active WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, simulation_id: str):
        """Accept a new WebSocket connection for a simulation."""
        await websocket.accept()
        
        if simulation_id not in self.active_connections:
            self.active_connections[simulation_id] = set()
        
        self.active_connections[simulation_id].add(websocket)
        logger.info(f"✅ WebSocket connected for simulation {simulation_id}")
    
    def disconnect(self, websocket: WebSocket, simulation_id: str):
        """Remove a WebSocket connection."""
        if simulation_id in self.active_connections:
            self.active_connections[simulation_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[simulation_id]:
                del self.active_connections[simulation_id]
        
        logger.info(f"❌ WebSocket disconnected for simulation {simulation_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast_to_simulation(self, simulation_id: str, message: dict):
        """
        Broadcast a message to all connections watching a specific simulation.
        
        Args:
            simulation_id: The simulation to broadcast to
            message: The message to send (will be JSON serialized)
        """
        if simulation_id not in self.active_connections:
            return
        
        # Create a copy of the set to avoid modification during iteration
        connections = list(self.active_connections[simulation_id])
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                # Remove dead connections
                self.disconnect(connection, simulation_id)


# Singleton instance
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the singleton ConnectionManager instance."""
    return manager

