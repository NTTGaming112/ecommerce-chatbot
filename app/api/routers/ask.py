from fastapi import APIRouter, HTTPException
from app.schemas import QueryInput, QueryResponse
from app.services.memory_service import memory_service
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Query"])


@router.post(
    "/ask",
    response_model=QueryResponse,
    summary="Multi-Agent Q&A: Supervisor → SearchAgent → AnswerAgent",
)
async def ask_question(query: QueryInput):
    """
    Multi-agent pipeline:
    - **Supervisor** phân loại intent và routing
    - **SearchAgent** tìm top-k docs (ChromaDB) hoặc web search (Tavily/DuckDuckGo)
    - **AnswerAgent** sinh câu trả lời theo mode shallow hoặc deep
    """
    try:
        session_id = query.session_id
        question = query.question
        search_mode = query.search_mode or "auto"

        # 1. Lấy lịch sử từ Redis buffer (nếu có) hoặc SQLite
        history = memory_service.get_history(session_id)

        # 2. Lấy summary từ Redis (nếu có)
        summary = memory_service.get_summary(session_id)

        # 3. Chạy Multi-Agent Pipeline (Supervisor → SearchAgent → AnswerAgent)
        answer, sources, intent, answer_mode, used_search_mode, confidence = llm_service.ask(
            question=question,
            history=history,
            session_id=session_id,
            summary=summary,
            search_mode=search_mode,
        )

        # 4. Lưu tin nhắn mới vào Redis buffer + SQLite
        memory_service.add_message(session_id, "user", question)
        memory_service.add_message(session_id, "bot", answer)

        return QueryResponse(
            answer=answer,
            sources=sources,
            intent=intent,
            answer_mode=answer_mode,
            search_mode=used_search_mode,
            confidence=confidence,
        )

    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/history/{session_id}",
    summary="Xóa lịch sử chat (Redis + SQLite)",
)
async def clear_history(session_id: str):
    try:
        memory_service.clear_history(session_id)
        return {"status": "success", "message": "Lịch sử đã được xóa"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
