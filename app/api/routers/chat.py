"""Chat API endpoints - Unified Multi-Agent Customer Support Pipeline."""
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents import router_agent
from app.agents.domain_fetcher import fetch_domain_context
from app.services.confirmation_service import confirmation_service
from app.services.database import db_service
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service

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


@router.post("/chat", response_model=ChatResponse, summary="Chat with Multi-Agent AI Support")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    customer_id = req.customer_id
    message = req.message.strip()

    try:
        logger.info("[ChatAPI] customer_id=%s session_id=%s message=%r", customer_id, session_id, message[:120])

        # 1. Kiểm tra Pending Action cần khách hàng xác nhận
        pending = confirmation_service.get_pending(session_id)
        if pending:
            if confirmation_service.is_confirm(message):
                action_type = pending["action_type"]
                payload = pending["payload"]
                confirmation_service.clear_pending(session_id)

                if action_type == "cancel_order":
                    res = db_service.cancel_order(payload["order_id"])
                    ans = f"Đơn hàng {payload['order_id']} đã được hủy thành công. Số tiền {res.get('total', 0):,}₫ sẽ được hoàn lại theo chính sách."
                    actions = ["OrderAgent.cancel_order"]
                elif action_type == "return_request":
                    from app.agents import refund_agent
                    res = refund_agent.create_return_request(
                        cid=customer_id,
                        oid=payload["order_id"],
                        items=payload.get("items", []),
                        confirmed=True,
                    )
                    ans = f"Yêu cầu trả hàng cho đơn {payload['order_id']} đã được tạo thành công (Mã yêu cầu: {res.get('return_id')}). Hướng dẫn: {res.get('instructions')}."
                    actions = ["RefundAgent.create_return_request"]
                else:
                    ans = "Yêu cầu của bạn đã được xác nhận và xử lý thành công."
                    actions = ["ConfirmationService.executed"]

                memory_service.add_message(session_id, "user", message)
                memory_service.add_message(session_id, "bot", ans)
                return ChatResponse(
                    answer=ans,
                    intent=action_type,
                    confidence=1.0,
                    actions_taken=actions,
                    entities=payload,
                    urgency="medium",
                    session_id=session_id,
                    needs_confirmation=False,
                )

            elif confirmation_service.is_reject(message):
                confirmation_service.clear_pending(session_id)
                ans = "Dạ vâng, tôi đã hủy thao tác này. Bạn có cần hỗ trợ thêm thông tin gì khác không?"
                memory_service.add_message(session_id, "user", message)
                memory_service.add_message(session_id, "bot", ans)
                return ChatResponse(
                    answer=ans,
                    intent="general",
                    confidence=1.0,
                    actions_taken=["ConfirmationService.cancelled"],
                    entities={},
                    urgency="low",
                    session_id=session_id,
                    needs_confirmation=False,
                )

        # 2. Phân loại ý định (Intent) và trích xuất thực thể (Entities)
        intent_info = router_agent.classify_intent(message)
        intent = intent_info.get("intent", "general")
        confidence = intent_info.get("confidence", 0.6)
        entities = router_agent.extract_entities(message, intent)
        urgency = router_agent.determine_urgency(message, intent)

        # 3. Tra cứu dữ liệu nghiệp vụ (Domain Data Context)
        domain_context, actions_taken = fetch_domain_context(customer_id, message, intent, entities)

        # 4. Kiểm tra nếu hành động có tính thay đổi dữ liệu cần xác nhận
        needs_confirmation = False
        if intent == "return_request" and entities.get("order_id") and any(w in message.lower() for w in ["muon tra", "doi hang", "tra lai", "tra ao", "tra quan"]):
            confirmation_service.set_pending(
                session_id=session_id,
                action_type="return_request",
                payload={"order_id": entities["order_id"]},
                prompt=f"Bạn có chắc muốn gửi yêu cầu trả hàng cho đơn {entities['order_id']} không?"
            )
            needs_confirmation = True

        # 5. Lấy lịch sử hội thoại
        history = memory_service.get_history(session_id)
        summary = memory_service.get_summary(session_id)

        # 6. Chạy Multi-Agent LLM Service (SearchAgent KB + AnswerAgent Grounded)
        answer, sources, detected_intent, answer_mode, search_mode, ans_conf = llm_service.ask(
            question=message,
            history=history,
            session_id=session_id,
            summary=summary,
            search_mode="vector",
            extra_context=domain_context,
        )

        # 7. Lưu tin nhắn vào persistent storage
        memory_service.add_message(session_id, "user", message)
        memory_service.add_message(session_id, "bot", answer)

        logger.info("[ChatAPI] done customer_id=%s intent=%s actions=%s", customer_id, intent, actions_taken)

        return ChatResponse(
            answer=answer,
            intent=intent,
            confidence=max(confidence, ans_conf),
            actions_taken=actions_taken,
            entities=entities,
            urgency=urgency,
            session_id=session_id,
            needs_confirmation=needs_confirmation,
        )

    except Exception as e:
        logger.exception("Chat failed for customer %s", customer_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools", summary="List all available tools")
async def list_tools():
    from app.tools import tool_registry
    return {"tools": tool_registry.list_tools()}