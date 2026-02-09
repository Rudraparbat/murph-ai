from fastapi import APIRouter
from src.controllers.agent_controllers import agent_router
from src.controllers.health_controllers import health_router
api_router = APIRouter(prefix="/api")

api_router.include_router(agent_router)
api_router.include_router(health_router)