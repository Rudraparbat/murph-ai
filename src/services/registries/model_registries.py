import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()


class ModelFactory :

    @staticmethod
    def load_model(model_details: dict, tools: list = None) -> ChatGroq: 
        try:
            provider = model_details.get('provider')
            if str(provider.get('name').upper()) == 'GROQ':
                api_key = os.getenv("GROQ_API_KEY")
                
                # 1. Initialize the base model
                llm = ChatGroq(api_key=api_key, model="openai/gpt-oss-120b")
                
                # 2. Bind the tools if they were provided
                if tools:
                    llm = llm.bind_tools(tools)
                    print(f"Tools successfully bound to {provider.get('name')}")
                
                return llm, None
            else:
                return None, "Unsupported Provider"
        except Exception as e:
            return None, str(e)
        
    # add more for other models