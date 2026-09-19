# Chat API endpoints
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.orchestrator import process_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])

class ChatRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=10000)
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    intent: str
    confidence: float
    actions_taken: List[str]
    entities: Dict[str, Any]
    urgency: str
    session_id: str = ""
    needs_confirmation: bool = False

@router.post("/chat", response_model=ChatResponse, summary="Chat with AI Customer Support")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    try:
        state = process_message(req.customer_id, req.message)
        return ChatResponse(
            answer=state.get("final_response", "I understand your request."),
            intent=state.get("intent", "general"),
            confidence=state.get("confidence", 0.5),
            actions_taken=state.get("actions", []),
            entities=state.get("entities", {}),
            urgency=state.get("urgency", "medium"),
            session_id=session_id,
        )
    except Exception as e:
        logger.exception("Chat failed for customer %s", req.customer_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools", summary="List all available tools")
async def list_tools():
    from app.tools import tool_registry
    return {"tools": tool_registry.list_tools()}