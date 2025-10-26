"""
WebSocket API Endpoints

Real-time updates for simulations via WebSocket.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.websocket import get_connection_manager
import asyncio
import json
import redis.asyncio as aioredis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/simulations/{simulation_id}")
async def websocket_simulation_updates(
    websocket: WebSocket,
    simulation_id: str
):
    """
    WebSocket endpoint for real-time simulation updates.
    
    Clients connect to this endpoint with a simulation_id and receive
    real-time progress updates as the simulation runs via Redis pub/sub.
    
    Message format:
    {
        "type": "progress" | "status" | "completed" | "error",
        "simulation_id": "uuid",
        "status": "RUNNING",
        "progress": 50,
        "message": "Processing..."
    }
    """
    await websocket.accept()
    
    # Create Redis connection for pub/sub
    redis_conn = aioredis.from_url(settings.REDIS_URL)
    pubsub = redis_conn.pubsub()
    
    # Subscribe to simulation updates
    channel = f"simulation:{simulation_id}"
    await pubsub.subscribe(channel)
    
    logger.info(f"✅ WebSocket connected for simulation {simulation_id}")
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "simulation_id": simulation_id,
            "message": f"Connected to simulation {simulation_id}"
        })
        
        # Listen for Redis pub/sub messages
        async def listen_redis():
            """Listen for Redis pub/sub messages and forward to WebSocket."""
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        # Parse the message
                        data = json.loads(message["data"])
                        # Forward to WebSocket client
                        await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error in Redis listener: {e}")
        
        # Listen for WebSocket messages (for ping/pong)
        async def listen_websocket():
            """Listen for WebSocket messages from client."""
            try:
                while True:
                    data = await websocket.receive_text()
                    if data == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "simulation_id": simulation_id
                        })
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Error in WebSocket listener: {e}")
        
        # Run both listeners concurrently
        await asyncio.gather(
            listen_redis(),
            listen_websocket(),
            return_exceptions=True
        )
    
    except WebSocketDisconnect:
        logger.info(f"❌ Client disconnected from simulation {simulation_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for simulation {simulation_id}: {e}")
    
    finally:
        # Cleanup
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await redis_conn.close()
        logger.info(f"🧹 Cleaned up WebSocket connection for simulation {simulation_id}")

