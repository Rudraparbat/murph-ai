from src.services.registries.graph_registry import get_or_build_graph
from fastapi.exceptions import HTTPException

class AgentService :

    @staticmethod
    async def invoke_message(config : dict) :
        try :
            graph = await get_or_build_graph(config)
            if not graph :
                raise HTTPException(400 , "Graph building failed")
            
            message = config.get('message')
            phone_number = config.get('phone_number')

            result = await graph.ainvoke(
            {"messages": [("user", message)],
            "phone_number": phone_number, 
            },
            config={"configurable": {"thread_id": phone_number}},  # using phone number as thread id with memory
            )

            response_text = result['messages'][-1].content

            return {"response": response_text}
        except Exception as e :
            raise HTTPException(400 , str(e))