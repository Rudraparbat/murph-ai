# src/utils/node_registry.py
import os
import httpx
from langchain_groq import ChatGroq
from typing import Callable
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from langchain_core.tools import tool
from pydantic import create_model, Field
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.prebuilt import InjectedState
from typing import Annotated
load_dotenv()
url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
api_key = os.getenv("API_KEY")
class GraphNodeFactory:
    """Factory to create graph nodes with shared LLM context"""
    

    @staticmethod
    def agent_node(llm , system_prompt) -> Callable:
        """Create agent node that uses LLM"""
        def _agent_node(state: MessagesState):
            messages = state['messages']
            
            print(f"I am sending the message from here")
            # Add system prompt
            if system_prompt:
                if not messages or messages[0].type != "system":
                    messages = [SystemMessage(content=system_prompt)] + list(messages)
        
            # Invoke LLM
            response = llm.invoke(messages)
            print(response)
            return {"messages": [response]}
        
        return _agent_node
    
    @staticmethod
    def final_node(config: dict , agent_id) -> Callable:
        async def _final_node(state):
            messages = state['messages']
            print("getting the config", config)
            print(f"Final Node Sending Message {messages}")
            print(f"I am sending the message from here")
            print(f"Agent id : {agent_id}")
            # Get the agent's response
            agent_response = messages[-1].content if messages else ''
            
            # Extract data from state
            phone_number = state.get('phone_number', '')
            
            # Perform your action (API call, send SMS, etc.)
            template_id = config.get('id')
            
            # Return properly formatted message
            headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            main_url = f"{url}/api/comms/send/message/"
            payload = {
                "to": phone_number ,
                "template_id": template_id ,
                "params": {"message" : agent_response},
                "agent_id": str(agent_id)
                }
            print(f"Template Id {template_id}")
            print(payload)
            try :
                async with httpx.AsyncClient() as client:
                    resp = await client.post(main_url, json = payload , headers=headers)
                    resp.raise_for_status()
                    print(resp.json())
                    return {"messages": [AIMessage(content="Message Sended")]}
            except Exception as e :
                print(str(e))
                return {"messages": [AIMessage(content="Message Cant Send Tool Execution Error")]}
        return  _final_node
