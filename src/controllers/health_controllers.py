import redis
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Dict, Any    

health_router = APIRouter()


@health_router.get("/health", status_code=200, summary="Health Check",
                  description="Simple health check that returns service status")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint that returns if the service is running.
    This endpoint should always return 200 if the service is up.
    """
    return {
        "status": "healthy",
        "service": "langraph-agent",
        "version": "v1"
    }