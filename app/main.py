# AI Customer Support Multi-Agent System
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routers import ask, chat, health, ingest
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Customer Support Multi-Agent System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (chat.router, ask.router, ingest.router, health.router):
    app.include_router(router)


@app.get("/")
def root():
    return {"message": "AI Customer Support Multi-Agent System", "version": "2.0.0", "docs": "/docs", "chat": "/chat"}


@app.get("/chat")
def chat_page():
    return FileResponse("app/static/chat.html")


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "agents": 10, "tools": 18}


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active = {}

    async def connect(self, ws, client_id):
        await ws.accept()
        self.active[client_id] = ws

    def disconnect(self, client_id):
        self.active.pop(client_id, None)

    async def send(self, client_id, data):
        ws = self.active.get(client_id)
        if ws:
            await ws.send_json(data)


ws_manager = ConnectionManager()


@app.websocket("/ws/chat/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            customer_id = data.get("customer_id", client_id)

            # Send typing indicator
            await ws_manager.send(client_id, {"type": "typing", "status": "processing"})

            # Process message
            from app.agents.orchestrator import process_message
            state = process_message(customer_id, message)

            # Send response
            await ws_manager.send(client_id, {
                "type": "response",
                "answer": state.get("final_response", ""),
                "intent": state.get("intent", ""),
                "confidence": state.get("confidence", 0),
                "actions_taken": state.get("actions", []),
                "entities": state.get("entities", {}),
                "urgency": state.get("urgency", "medium"),
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
