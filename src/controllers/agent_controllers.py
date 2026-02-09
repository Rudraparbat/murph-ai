import logging
from fastapi import APIRouter
from pydantic import BaseModel
from src.services.ai_service import   AgentService
logger = logging.getLogger(__name__)

agent_router = APIRouter(tags=["agent-router"])

class ChatReuestSchema(BaseModel) :
    agent_id : str 
    phone_number : str 
    message : str

@agent_router.post('/chat')
async def chat(request: ChatReuestSchema): 
    config = {
       "agent_id" : request.agent_id ,
       "phone_number" :  request.phone_number , 
       "message" : request.message
    }
    print(f"Recieved config {config}")
    return await AgentService.invoke_message(config)
