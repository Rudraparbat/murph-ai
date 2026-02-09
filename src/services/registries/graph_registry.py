# src/graph_builder.py (Updated)
import json
import os
import httpx
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
from async_lru import alru_cache
from langgraph.graph import MessagesState
from .model_registries import ModelFactory 
from .node_registry import GraphNodeFactory 
from .tool_registry import ToolsFactory
from typing import Literal
from langgraph.checkpoint.memory import InMemorySaver  
load_dotenv()
url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
api_key = os.getenv("API_KEY")


class APIMessagesState(MessagesState):
    """Extended state for API mode with additional context"""
    phone_number: str = ""


class AiBuilder:
    def __init__(self, agent_id, room_id=None, mode: Literal["websocket", "api"] = "websocket"):
        self.agent_id = agent_id
        self.room_id = room_id
        self.mode = mode  # New: differentiate between websocket and api

    async def build_graph(self, llm, prompt: str, tools: list = None, finish_node = None):
        """
        Build graph based on mode:
        - websocket: agent ↔ conditional_tools (loop)
        - api: agent → conditional_tools → final_tool → END (linear)
        """
        try:
            workflow = StateGraph(APIMessagesState)
            
            # Add agent node
            workflow.add_node("agent", GraphNodeFactory.agent_node(llm , prompt))
            
            # Add conditional tools if available
            if tools:
                tool_node_instance = ToolNode(tools, handle_tool_errors=True)
                workflow.add_node("tools", tool_node_instance)
                print(f"Created conditional tool node with {len(tools)} tools")
            
            if finish_node :
                workflow.add_node("finish_node" , finish_node)
                print(f"Finish Node Added Successfully for the graph")
            # Build edges based on mode
            workflow.add_edge(START, "agent")
            if self.mode == "websocket":
                # WebSocket: agent ↔ tools (loop back)
                if tools:
                    workflow.add_conditional_edges("agent", tools_condition)
                    workflow.add_edge("tools", "agent")
                else:
                    workflow.add_edge("agent", END)
                    
            elif self.mode == "api":
                # API: agent → tools → final_tool → END (linear flow)
                if tools and finish_node :
                    def route_after_agent(state: APIMessagesState) -> str:
                        """Route to tools if LLM called them, otherwise directly to finish_node"""
                        last_message = state['messages'][-1]
                        
                        # Check if LLM called any tools
                        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                            print(" LLM called tools, routing: agent → tools")
                            return "tools"
                        
                        # No tools called, go directly to finish_node
                        print(" No tools called, routing: agent → finish_node")
                        return "finish_node"
                    
                    # Agent can call conditional tools
                    workflow.add_conditional_edges(
                        "agent",
                        route_after_agent,
                        {
                            "tools": "tools",
                            "finish_node": "finish_node"
                        }
                    )
                    # After tools, always go to final_tool
                    workflow.add_edge("tools", "finish_node")
                    # Final tool ends the flow
                    workflow.add_edge("finish_node", END)
                elif finish_node:
                    # No conditional tools, just agent → final_tool
                    workflow.add_edge("agent", "finish_node")
                    workflow.add_edge("finish_node", END)
                else:
                    # Fallback: just end
                    workflow.add_edge("agent", END)    
            
            checkpointer = InMemorySaver()  
            graph = workflow.compile(checkpointer=checkpointer)
            print(f"Graph built successfully in {self.mode} mode")
            try:
                print("\n" + "="*60)
                print(f"GRAPH STRUCTURE ({self.mode} mode):")
                print("="*60)
                
                # Method 1: Print as Mermaid diagram
                mermaid_diagram = graph.get_graph().draw_mermaid()
                print(mermaid_diagram)
                print("="*60 + "\n")
                
            except Exception as viz_error:
                print(f"Could not visualize graph: {viz_error}")
            
            return graph, None
            
        except Exception as e:
            print(f"Graph build error: {e}")
            return None, str(e)

    async def _get_agent_by_id(self):
        try:
            main_url = f"{url}/api/live/agent/{self.agent_id}/"
            headers = {
                    "Authorization": (
                        f"Bearer {api_key}"

                    ),
                    "Content-Type": "application/json",
            }
            async with httpx.AsyncClient() as client:
                resp = await client.get(main_url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data, None
        except Exception as e:
            return None, str(e)

    async def fetch_openai_functions(self, comm_ids):
        try:
            main_url = f"{url}/api/comms/communication-templates/{comm_ids}/openai_functions/"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient() as client:
                resp = await client.get(main_url, headers=headers)
                resp.raise_for_status()
                return resp.json(), None
        except Exception as e:
            return None, str(e)

    async def build_ai(self):
        try:
            agent, error = await self._get_agent_by_id()
            if error is not None:
                print(f"Error in fetching agent: {error}")
                return None

            conditional_tools = []  # Tools for conditional execution
            finish_node = None       # Final tool for API mode
            
            # Build the function call tools
            if agent.get('comms_templates_registered_detail'):
                print(f"Received Comms Tools List: {agent.get('comms_templates_registered')}")

                for comms in agent.get('comms_templates_registered_detail'):
                    res, error = await self.fetch_openai_functions(comms.get('id'))
                    
                    if error:
                        print(f"Error fetching functions for {comms.get('id')}: {error}")
                        continue
                    
                    print("Fetched Function:", res)
                    function_schema = res.get('functions', [{}])[0]
                    template_type = comms.get('template_type')
                    
                    # if its a system template then its a graph node for api mode
                    if self.mode == "api" and template_type == 'System Template':
                        finish_node = GraphNodeFactory.final_node(comms , self.agent_id)
                    else :
                        comm_tool = ToolsFactory.tool_node(
                        function_schema, 
                        comms.get('id'),
                        template_type
                        )
                        conditional_tools.append(comm_tool)
                        print(f"Added {comm_tool.name} as conditional tool")
            
            print(f"Successfully created {len(conditional_tools)} conditional tools")
            if finish_node :
                print(f"Final tool: {finish_node.__name__}")

            # Load model
            model_details = agent.get('chat_configuration', {}).get('llm_model_detail')
            if not model_details:
                print("Only Chat Model Supported")
                return None
            
            # Bind all tools to LLM (both conditional and final)
            all_tools = conditional_tools 
            llm_model, error = ModelFactory.load_model(model_details, all_tools)
            print(f"LLM Model GENERATED: {llm_model}")
            
            if error is not None:
                print(f"Error loading model: {error}")
                return None
            
            # Build the graph
            system_prompt = agent.get('active_prompt', {}).get('prompt')
            print(f"System prompt received: {system_prompt[:100]}...")  # Print first 100 chars
            
            graph_obj, error = await self.build_graph(
                llm_model, 
                system_prompt, 
                conditional_tools if conditional_tools else None,
                finish_node
            )
            
            if error is not None:
                print(f"Error building graph: {error}")
                return None
            
            return graph_obj
            
        except Exception as e:
            print(f"Error in build_ai: {e}")
            import traceback
            traceback.print_exc()
            return None




@alru_cache(maxsize=128, ttl=300)
async def _cached_build_graph(agent_id: str):
    """Cache for API graphs"""
    ai = AiBuilder(agent_id, mode="api")
    graph = await ai.build_ai()
    return graph


async def get_or_build_graph(config: dict):
    agent_id = config.get("agent_id")

    # Optional: inspect cache stats
    info_before = _cached_build_graph.cache_info()
    print(f"[before] cache info for _cached_build_graph: {info_before}")

    graph = await _cached_build_graph(agent_id)

    info_after = _cached_build_graph.cache_info()
    print(f"[after]  cache info for _cached_build_graph: {info_after}")

    if info_after.hits > info_before.hits:
        print(f" Graph for agent {agent_id} returned from cache")
    else:
        print(f"Graph for agent {agent_id} built fresh")

    if graph is None:
        print(f"Failed to build graph for agent: {agent_id}")
        return None
    return graph

