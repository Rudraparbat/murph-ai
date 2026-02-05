from typing import Annotated
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START , END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
from langgraph.graph import MessagesState
load_dotenv()
from langchain_core.messages import AIMessage

def research_node(state: MessagesState):
    # We append a message to the 'messages' list
    print(f"Research Node State Messages: {state['messages']}")
    return {"messages": [AIMessage(content="Research: Mars is red.")]}

def fact_check_node(state: MessagesState):
    # This runs in parallel and also appends to 'messages'
    print(f"Fact Check Node State Messages: {state['messages']}")
    return {"messages": [AIMessage(content="Fact: Mars has 2 moons.")]}

def final_node(state: MessagesState):
    # Both messages above will be inside state["messages"] automatically
    print(f"Final Node State Messages: {state['messages']}")
    all_content = [m.content for m in state["messages"]]
    return {"messages": [AIMessage(content=f"Combined: {' '.join(all_content)}")]}

# testing purpose
def load_model(api_key : str) -> ChatGroq : 
    try :
        llm = ChatGroq(api_key=api_key, model="openai/gpt-oss-120b")
        return llm , None
    except Exception as e :
        return None , str(e)

def build_graph() :
    graph = StateGraph(MessagesState)
    print("Adding Nodes")
    graph.add_node('research_node' , research_node) #
    print(f"Research Node Added Successfully")
    graph.add_node('fact_check_node' , fact_check_node) #
    print(f"Fact Check Node Added Successfully")
    graph.add_node('final_node' , final_node)
    print(f"Final Node Addedd Successfully")
    graph.add_edge(START , 'research_node')
    graph.add_edge(START , 'fact_check_node')
    graph.add_edge(['research_node' , 'fact_check_node'] , 'final_node')
    graph.add_edge('final_node' , END)
    print(f"Edges Addedd Successfully")

    main_graph = graph.compile()
    return main_graph

def chat(llm : ChatGroq , message : str) -> None :
    try :
        response = llm.stream(message)
        for chunk in response:
            print(chunk.content, end="", flush=True)
    except Exception as e :
        return None , str(e)
    
def main():
    # load the
    api_key = os.getenv("GROQ_API_KEY")
    print(f"Using API Key : {api_key}")
    print("Loading model...")
    llm , error = load_model(api_key)
    if error :
        print(f"Error loading model : {error}")
        return 
    
    print("Model loaded successfully , Start Chating...")

    graph = build_graph()
    resp = graph.invoke({"messages": [AIMessage(content="Tell me about Mars.")]})
    print(resp["messages"][-1].content)

    # while True :
    #     message = input("You : ")
    #     if message.lower() in ["exit" , "quit"] :
    #         print("Exiting...")
    #         break 
    #     chat(llm , message)
