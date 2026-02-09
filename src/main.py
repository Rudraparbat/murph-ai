"""
FastAPI Application Initialization

This script sets up the FastAPI app, configures settings,
and imports required modules (models, views, and routes).
"""

from collections import defaultdict
import os
from fastapi import FastAPI, WebSocket , WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.routes.main_route import api_router
SECRET_KEY = os.urandom(32)

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    expose_headers=["*"],
    max_age=600,
)


app.include_router(
    api_router
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Langraph API!"}



  


# from fastapi.responses import HTMLResponse 

# @app.get("/chatpage/") 
# async def htmlview() :
#     return HTMLResponse(html)





# class ConnectionManager :
#   def __init__(self):
#     self.active_user : dict[str, list[WebSocket]] = defaultdict(list)

#   async def connect(self , agent_id ,  websocket : WebSocket) :
#     self.chat_room_id = f"AGENT--{agent_id}"
#     print(f"Chat id {self.chat_room_id}")
#     # fetch the agent and build it 
#     ai = AiBuilder(agent_id , self.chat_room_id , 'websocket')
#     main_graph = await ai.build_ai()
#     print(f"Graph Received {main_graph}")
#     if main_graph is None :
#        await self.disconnect(websocket)
#     self.ai = main_graph
#     print("AI Initialized Successfully")
#     self.active_user[self.chat_room_id].append(websocket)

#   async def disconnect(self , websocket : WebSocket) :
#     print(f"Start Disconnecting it")
 
#   async def broadcast(self ,  message : str) :
#     response = await self.ai.ainvoke(
#         {"messages": [("user", message)]},
#         config={"configurable": {"thread_id": self.chat_room_id}}
#        )
#     result = response['messages'][-1].content
#     for connections in self.active_user[self.chat_room_id] :
#       try :
#         await connections.send_text(result)
#       except Exception as e :
#          self.disconnect(connections)
      


# manager = ConnectionManager()


# @app.websocket("/ws/chat/") 
# async def websocketendpoint(websocket : WebSocket) :
#     # accept the wesocket conn
#     await websocket.accept() 
#     agent_id = websocket.query_params.get("id")
#     print("Agent id" , agent_id)
#     await manager.connect(agent_id , websocket)
#     try :
#         while True :
#             data = await websocket.receive_text()
#             await manager.broadcast(data)
#     except WebSocketDisconnect :
#         await manager.disconnect(websocket)
