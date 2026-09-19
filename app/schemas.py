from typing import List, Literal

from pydantic import BaseModel, Field


RequestedSearchMode = Literal["auto", "vector", "web", "hybrid"]
UsedSearchMode = Literal["none", "vector", "web", "hybrid"]
Intent = Literal["greeting", "general", "retrieval", "web_search"]
AnswerMode = Literal["shallow", "deep"]


class DocumentInput(BaseModel):
    document_id: str = Field(min_length=1, max_length=256)
    text_content: str = Field(min_length=1, max_length=1_000_000)


class QueryInput(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    question: str = Field(min_length=1, max_length=10_000)
    search_mode: RequestedSearchMode = "auto"


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    intent: Intent = "general"
    answer_mode: AnswerMode = "shallow"
    search_mode: UsedSearchMode = "none"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class HealthResponse(BaseModel):
    status: str
    redis_available: bool
    chroma_ok: bool
    llm_ok: bool
