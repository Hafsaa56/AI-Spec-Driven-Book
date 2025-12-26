from fastapi import APIRouter
from typing import Dict, Any
import time
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    services: Dict[str, Any]

class ReadinessResponse(BaseModel):
    ready: bool
    services: Dict[str, Any]

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check for the entire application."""
    # Check if all services are available
    services_status = {
        "api": "healthy",
        "database": "not_connected",  # Will be updated when connected
        "vector_db": "not_connected",  # Will be updated when connected
        "llm_service": "not_connected"  # Will be updated when connected
    }
    
    # In a real implementation, we would check actual service connectivity
    # For now, we'll just return a basic health status
    
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        services=services_status
    )

@router.get("/readiness", response_model=ReadinessResponse)
async def readiness_check():
    """Readiness check to see if the application is ready to serve traffic."""
    # Check if all required services are ready
    # For now, we'll assume the application is ready
    services_status = {
        "api": "ready",
        "database": "not_connected",
        "vector_db": "not_connected",
        "llm_service": "not_connected"
    }
    
    return ReadinessResponse(
        ready=True,  # In a real app, this would check actual service status
        services=services_status
    )

@router.get("/liveness", response_model=HealthResponse)
async def liveness_check():
    """Liveness check to see if the application is alive."""
    return HealthResponse(
        status="alive",
        timestamp=time.time(),
        services={"api": "running"}
    )
