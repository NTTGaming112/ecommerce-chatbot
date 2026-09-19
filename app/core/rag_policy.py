"""Pure routing rules for the grounded RAG workflow."""
from dataclasses import dataclass
import re
from typing import Literal


Intent = Literal["greeting", "general", "retrieval", "web_search"]
RequestedSearchMode = Literal["auto", "vector", "web", "hybrid"]
UsedSearchMode = Literal["none", "vector", "web", "hybrid"]
AnswerMode = Literal["shallow", "deep"]


@dataclass(frozen=True)
class RouteDecision:
    intent: Intent
    search_mode: UsedSearchMode
    answer_mode: AnswerMode


_GREETING_ONLY = re.compile(
    r"^\s*(?:(?:xin\s+)?chào|hello|hi|hey|good\s+(?:morning|afternoon|evening))"
    r"(?:\s+(?:bạn|mọi\s+người|anh|chị|em))?[!,.?…\s]*$",
    re.IGNORECASE,
)
_IDENTITY_QUESTION = re.compile(
    r"^\s*(?:bạn\s+là\s+ai|bạn\s+tên\s+gì|who\s+are\s+you|what(?:'s|\s+is)\s+your\s+name)"
    r"[!,.?…\s]*$",
    re.IGNORECASE,
)
_WEB_SEARCH_REQUEST = re.compile(
    r"\b(?:tìm\s+trên\s+mạng|search\s+web|google|tin\s+tức|news|mới\s+nhất|latest|hôm\s+nay|today|hiện\s+tại|current)\b",
    re.IGNORECASE,
)


def is_greeting(question: str) -> bool:
    """Return true only for a standalone greeting or identity question."""
    return bool(_GREETING_ONLY.fullmatch(question) or _IDENTITY_QUESTION.fullmatch(question))


def requests_web_search(question: str) -> bool:
    return bool(_WEB_SEARCH_REQUEST.search(question))


def resolve_route(intent: Intent, requested_mode: RequestedSearchMode) -> RouteDecision:
    """Apply explicit user choice first, then the strict grounded defaults."""
    if requested_mode == "vector":
        return RouteDecision("retrieval", "vector", "deep")
    if requested_mode in {"web", "hybrid"}:
        return RouteDecision("web_search", requested_mode, "deep")
    if intent == "greeting":
        return RouteDecision("greeting", "none", "shallow")
    if intent == "web_search":
        return RouteDecision("web_search", "web", "deep")

    return RouteDecision("retrieval", "vector", "deep")
