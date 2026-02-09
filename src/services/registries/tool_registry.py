import os
import httpx
from typing import Callable
from langchain_core.tools import tool
from pydantic import create_model, Field
from dotenv import load_dotenv
from langgraph.prebuilt import InjectedState
from typing import Annotated
load_dotenv()
url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


class ToolsFactory :

    @staticmethod
    def _create_field_definitons(schema_dict: dict) -> dict :
        try :
            name = schema_dict["name"]
            description = schema_dict["description"]
            params = schema_dict["parameters"]
            properties = params.get("properties", {})
            required_fields = params.get("required", [])

            desc = (
                        "INTERNAL FIELD. Do not ask the user for this. "
                        "The system pulls this internally automatically. "
                        "Only ask the user for a phone number if the tool returns a 'missing number' error."
                    )
            
            properties['to']['description'] = desc
            print(f"new description for to {properties['to']['description']}")
            type_map = {
                "string": str,
                "integer": int,
                "number": float,
                "boolean": bool,
                "array": list,
                "object": dict
            }

            field_definitions = {}
            for prop_name, prop_info in properties.items():
                field_type = type_map.get(prop_info.get("type"), str)
                if prop_name == "to":
                    default_val = None 
                else:
                    default_val = ... if prop_name in required_fields else None
                field_definitions[prop_name] = (
                    field_type, 
                    Field(default=default_val, description=prop_info.get("description", ""))
                )
            
            return {
                'def' : field_definitions , 
                'name' : name ,
                'desc' : description
            }
        except Exception as e :
            raise ValueError(str(e))            



    @staticmethod
    def tool_node(schema_dict: dict, template_id: str, template_type: str = None) -> Callable:
        """Create tool node that uses LLM"""

        
        field_defs = ToolsFactory._create_field_definitons(schema_dict)
        field_definitions : dict  = field_defs.get('def')
        name : str = field_defs.get('name')
        description : str = field_defs.get('desc')
        print("Required Fields", field_definitions)
        DynamicInputModel = create_model(f"{name}_input", **field_definitions)
            
        def _tool_logic(state: Annotated[dict, InjectedState] , **kwargs):
            print(f'Logic execution start for tool: {name}')
            url = "https://120.123.21/something/"
            print(f"Template ID: {template_id}")
            print(f"Template Type: {template_type}")
            print(f"Tool arguments: {kwargs}")
            
            payload = {
                "template": template_id,
                "data": kwargs,
            }
            phone_from_state = state.get('phone_number')
            phone_from_llm = kwargs.get('to')
            
            target_phone = phone_from_state or phone_from_llm

            if not target_phone:
                # Tell the LLM exactly what went wrong
                return (f"Error: Target phone number ('to') is missing. "
                        f"It was not in the system state, and you didn't provide it. "
                        f"Please ask the user for their phone number.")

            print(f"Executing {name} for: {target_phone}")

            print(f"Targeting Phone Number: {target_phone}")
    
            return f"Tool {name} executed successfully with data: {kwargs}"
            
        _tool_logic.__name__ = name
        _tool_logic.__doc__ = description

        created_tool = tool(_tool_logic, args_schema=DynamicInputModel)
        
        return created_tool

