"""
Answer Agent - Chuyên sinh câu trả lời
================================================================
Tools:
  1. shallow_answer(question, history, summary)
     → Trả lời nhanh từ LLM knowledge, không cần context
     → Dùng cho: greeting, general knowledge, chitchat

  2. deep_answer(question, context, history, summary)
     → Reasoning với context từ Search Agent
     → Trả lời chi tiết, có trích dẫn nguồn
     → Dùng cho: câu hỏi cần tài liệu, thông tin cụ thể

  3. cite_sources(answer, sources)
     → Format câu trả lời kèm danh sách nguồn tham khảo

Graph flow:
  START → choose_mode → [shallow_node | deep_node] → cite_node → END
"""
import logging
from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.core.config import settings
from app.core.prompts import (
    GREETING_SYSTEM_PROMPT,
    GROUNDING_ABSTENTION,
    GROUNDING_SYSTEM_PROMPT,
    evidence_message,
    question_message,
    summary_message,
)

logger = logging.getLogger(__name__)


# ── State ──────────────────────────────────────────────────────────────────────

class AnswerState(TypedDict):
    question: str
    context: str
    history: List[dict]
    summary: Optional[str]
    intent: str                # "greeting" | "general" | "retrieval" | "web_search"
    answer_mode: str           # "shallow" | "deep"
    raw_answer: str
    answer: str                # Final formatted answer
    citations: List[str]       # Formatted citation list
    confidence: float          # 0.0 - 1.0
    evidence_confidence: float


# ── Tools (pure functions) ─────────────────────────────────────────────────────

def _build_messages(
    system_prompt: str,
    question: str,
    history: List[dict],
    summary: Optional[str] = None,
    context: str = "",
) -> list:
    messages = [SystemMessage(content=system_prompt)]

    if summary:
        messages.append(HumanMessage(content=summary_message(summary)))

    for message in history[-10:]:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        else:
            messages.append(AIMessage(content=message["content"]))

    if context:
        messages.append(HumanMessage(content=evidence_message(context)))

    messages.append(HumanMessage(content=question_message(question)))
    return messages


def shallow_answer(
    llm: ChatGoogleGenerativeAI,
    question: str,
    history: List[dict],
    summary: Optional[str] = None,
    intent: str = "general",
    context: str = "",
    evidence_confidence: float = 0.0,
) -> dict:
    if not context and intent != "greeting":
        return {"answer": GROUNDING_ABSTENTION, "confidence": 0.0}

    system_prompt = GROUNDING_SYSTEM_PROMPT if context else GREETING_SYSTEM_PROMPT
    try:
        response = llm.invoke(_build_messages(system_prompt, question, history, summary, context))
        confidence = evidence_confidence if context else 0.9
        return {"answer": response.content, "confidence": confidence}
    except Exception as e:
        logger.error(f"[AnswerAgent] shallow_answer error: {e}")
        return {"answer": "Xin lỗi, tôi gặp sự cố khi xử lý. Vui lòng thử lại.", "confidence": 0.0}


def deep_answer(
    llm: ChatGoogleGenerativeAI,
    question: str,
    context: str,
    history: List[dict],
    summary: Optional[str] = None,
    evidence_confidence: float = 0.0,
) -> dict:
    if not context:
        return {"answer": GROUNDING_ABSTENTION, "confidence": 0.0}

    try:
        response = llm.invoke(_build_messages(
            GROUNDING_SYSTEM_PROMPT,
            question,
            history,
            summary,
            context,
        ))
        return {"answer": response.content, "confidence": evidence_confidence}
    except Exception as e:
        logger.error(f"[AnswerAgent] deep_answer error: {e}")
        return {"answer": "Xin lỗi, tôi gặp sự cố khi xử lý câu hỏi. Vui lòng thử lại.", "confidence": 0.0}


def cite_sources(answer: str, sources: List[str]) -> str:
    """
    Tool 3: Format câu trả lời kèm danh sách nguồn tham khảo.
    Chỉ thêm citations nếu có nguồn thực sự.
    Returns: formatted answer string
    """
    if not sources:
        return answer

    # Lọc bỏ các sources rỗng hoặc không hợp lệ
    valid_sources = [s for s in sources if s and s.strip() and s != "unknown"]
    if not valid_sources:
        return answer

    citation_block = "\n\n---\n**Nguồn tham khảo:**"
    for i, src in enumerate(valid_sources[:5], 1):  # Max 5 nguồn
        citation_block += f"\n[{i}] {src}"

    return answer + citation_block


# ── Answer Agent Class ─────────────────────────────────────────────────────────

class AnswerAgent:
    """
    LangGraph agent chuyên sinh câu trả lời.
    Được gọi bởi Supervisor sau khi Search Agent hoàn thành.
    """

    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                google_api_key=settings.GOOGLE_API_KEY,
            )
            self.graph = self._build_graph()
            logger.info("[AnswerAgent] Initialized successfully.")
        except Exception as e:
            logger.error(f"[AnswerAgent] Initialization failed: {e}")
            self.llm = None
            self.graph = None

    # -- Nodes --

    def _choose_mode_node(self, state: AnswerState) -> dict:
        """Node: Xác nhận answer_mode (đã được set bởi Supervisor)"""
        logger.info(f"[AnswerAgent] mode={state['answer_mode']}, intent={state['intent']}")
        return {}

    def _shallow_node(self, state: AnswerState) -> dict:
        """Node: Gọi tool shallow_answer (có thể kèm context từ docs)"""
        result = shallow_answer(
            llm=self.llm,
            question=state["question"],
            history=state.get("history", []),
            summary=state.get("summary"),
            intent=state.get("intent", "general"),
            context=state.get("context", ""),
            evidence_confidence=state.get("evidence_confidence", 0.0),
        )
        return {"raw_answer": result["answer"], "confidence": result["confidence"]}

    def _deep_node(self, state: AnswerState) -> dict:
        """Node: Gọi tool deep_answer"""
        result = deep_answer(
            llm=self.llm,
            question=state["question"],
            context=state.get("context", ""),
            history=state.get("history", []),
            summary=state.get("summary"),
            evidence_confidence=state.get("evidence_confidence", 0.0),
        )
        return {"raw_answer": result["answer"], "confidence": result["confidence"]}

    def _cite_node(self, state: AnswerState) -> dict:
        """Node: Gọi tool cite_sources để format câu trả lời cuối cùng"""
        sources_to_cite = []
        if state.get("context"):
            sources_to_cite = state.get("citations", [])

        formatted = cite_sources(state["raw_answer"], sources_to_cite)
        return {"answer": formatted}

    # -- Routing --

    def _decide_answer_mode(self, state: AnswerState) -> str:
        if state.get("answer_mode") == "deep":
            return "deep"
        return "shallow"

    # -- Graph --

    def _build_graph(self) -> StateGraph:
        """
        START → choose_mode → [shallow_node | deep_node] → cite_node → END
        """
        g = StateGraph(AnswerState)

        g.add_node("choose_mode", self._choose_mode_node)
        g.add_node("shallow", self._shallow_node)
        g.add_node("deep", self._deep_node)
        g.add_node("cite", self._cite_node)

        g.set_entry_point("choose_mode")

        g.add_conditional_edges(
            "choose_mode",
            self._decide_answer_mode,
            {
                "shallow": "shallow",
                "deep": "deep",
            }
        )

        g.add_edge("shallow", "cite")
        g.add_edge("deep", "cite")
        g.add_edge("cite", END)

        return g.compile()

    # -- Public API --

    def answer(
        self,
        question: str,
        context: str = "",
        history: List[dict] = None,
        summary: Optional[str] = None,
        intent: str = "general",
        answer_mode: str = "shallow",  # "shallow" nếu có docs, "deep" nếu không có
        sources: List[str] = None,
        evidence_confidence: float = 0.0,
    ) -> dict:
        """
        Chạy answer workflow.
        Returns: {"answer": str, "confidence": float}
        """
        if not self.graph:
            raise RuntimeError("[AnswerAgent] Graph not initialized")

        initial_state = AnswerState(
            question=question,
            context=context,
            history=history or [],
            summary=summary,
            intent=intent,
            answer_mode=answer_mode,
            raw_answer="",
            answer="",
            citations=sources or [],
            confidence=0.0,
            evidence_confidence=evidence_confidence,
        )
        result = self.graph.invoke(initial_state)
        return {
            "answer": result.get("answer", ""),
            "confidence": result.get("confidence", 0.0),
        }


# Singleton
answer_agent = AnswerAgent()
