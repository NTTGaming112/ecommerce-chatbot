# AI Customer Support Multi-Agent System
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routers import ask, chat, ecommerce, health, ingest
from app.core.config import settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.services.database import db_service
        db_service.init_db()
        from app.services.retrieval_service import retrieval_service
        retrieval_service.sync_kb_from_db()
    except Exception as e:
        logging.warning("Startup KB/DB sync notice: %s", e)
    yield

app = FastAPI(title="AI Customer Support Multi-Agent System", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (chat.router, ecommerce.router, ask.router, ingest.router, health.router):
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

            # Process message with unified multi-agent chat pipeline
            from app.api.routers.chat import chat as process_chat, ChatRequest
            res = await process_chat(ChatRequest(customer_id=customer_id, message=message, session_id=client_id))

            # Send response
            await ws_manager.send(client_id, {
                "type": "response",
                "answer": res.answer,
                "intent": res.intent,
                "confidence": res.confidence,
                "actions_taken": res.actions_taken,
                "entities": res.entities,
                "urgency": res.urgency,
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
