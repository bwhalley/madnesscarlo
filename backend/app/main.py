"""
MTG Madness Carlo - Backend API

FastAPI application for running MTG deck simulations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Create FastAPI app
app = FastAPI(
    title="MTG Madness Carlo API",
    description="Monte Carlo simulation API for Magic: The Gathering deck analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint - API status"""
    return {
        "message": "MTG Madness Carlo API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "madness-carlo-api"
    }


# API info endpoint
@app.get("/api/info")
def api_info():
    """Get API information"""
    return {
        "name": "MTG Madness Carlo API",
        "version": "1.0.0",
        "features": [
            "Deck Management",
            "Monte Carlo Simulation",
            "Deck Comparison",
            "Experiment Framework",
            "Real-time Progress Updates"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": "/api"
        }
    }


# Run with: uvicorn app.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

