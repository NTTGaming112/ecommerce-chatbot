from fastapi import APIRouter
from app.schemas import HealthResponse
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check():
    memory_health = memory_service.health_check()
    chroma_ok = retrieval_service.vector_store is not None
    llm_ok = llm_service.is_ready
    status = "ok" if memory_health.get("sqlite_ok") and chroma_ok and llm_ok else "degraded"
    return HealthResponse(
        status=status,
        redis_available=memory_health.get("redis_available", False),
        chroma_ok=chroma_ok,
        llm_ok=llm_ok,
    )
