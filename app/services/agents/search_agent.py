"""
Search Agent - Chuyên tìm kiếm tài liệu và thông tin web
================================================================
Tools:
  1. retrieve_docs(query, k)      → Top-k docs từ ChromaDB (vector search)
  2. google_search(query, k)      → Web search qua Tavily (fallback: DuckDuckGo)
  3. rerank_docs(docs, query)     → Rerank kết quả theo relevance score

Graph flow:
  START → dispatch → [retrieve_node | web_search_node | hybrid_node] → rerank_node → END
"""
import logging
from typing import TypedDict, List, Optional, Annotated
import operator

from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.services.retrieval_service import retrieval_service

logger = logging.getLogger(__name__)


# ── State ──────────────────────────────────────────────────────────────────────

class SearchState(TypedDict):
    query: str
    search_mode: str                     # "vector" | "web" | "hybrid"
    retrieved_docs: List[dict]
    web_results: List[dict]
    final_context: str
    sources: List[str]
    doc_count: int                       # Số docs tìm được
    evidence_confidence: float


# ── Tools (pure functions) ─────────────────────────────────────────────────────

def retrieve_docs(query: str, k: int = None) -> List[dict]:
    """
    Tool 1: Tìm top-k documents từ ChromaDB bằng vector similarity search.
    Returns list of dicts với keys: content, document_id, chunk_index, score
    """
    k = k or settings.SEARCH_K
    try:
        scored_docs = retrieval_service.retrieve(query, k=k)
        results = []
        for doc, score in scored_docs:
            score = float(score)
            if score < settings.MIN_RETRIEVAL_SCORE:
                continue
            results.append({
                "content": doc.page_content,
                "document_id": doc.metadata.get("document_id", "unknown"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "source": f"DocID:{doc.metadata.get('document_id', 'unknown')}",
                "score": score,
            })
        logger.info(f"[SearchAgent] retrieve_docs: found {len(results)} docs for query='{query[:50]}'")
        return results
    except Exception as e:
        logger.error(f"[SearchAgent] retrieve_docs error: {e}")
        return []


def google_search(query: str, max_results: int = None) -> List[dict]:
    """
    Tool 2: Tìm kiếm web.
    Priority: Tavily API → DuckDuckGo fallback
    Returns list of dicts với keys: content, url, title, score
    """
    max_results = max_results or settings.WEB_SEARCH_MAX_RESULTS

    # --- Thử Tavily trước (tốt hơn, có snippet đầy đủ) ---
    if settings.TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(query, max_results=max_results)
            results = []
            for r in response.get("results", []):
                results.append({
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "source": r.get("url", ""),
                    "score": r.get("score", 0.5),
                })
            logger.info(f"[SearchAgent] google_search (Tavily): {len(results)} results")
            return results
        except Exception as e:
            logger.warning(f"[SearchAgent] Tavily search failed, falling back to DuckDuckGo: {e}")

    # --- Fallback: DuckDuckGo ---
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "content": r.get("body", ""),
                    "url": r.get("href", ""),
                    "title": r.get("title", ""),
                    "source": r.get("href", ""),
                    "score": 0.5,
                })
        logger.info(f"[SearchAgent] google_search (DuckDuckGo): {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"[SearchAgent] DuckDuckGo search failed: {e}")
        return []


def rerank_docs(docs: List[dict], query: str) -> List[dict]:
    """
    Tool 3: Rerank danh sách docs theo relevance với query.
    - Nếu RERANK_ENABLED=True: dùng cross-encoder model (cần sentence-transformers)
    - Fallback: simple keyword overlap scoring
    """
    if not docs:
        return docs

    if settings.RERANK_ENABLED:
        try:
            from sentence_transformers import CrossEncoder
            model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            pairs = [(query, doc["content"]) for doc in docs]
            scores = model.predict(pairs)
            for doc, score in zip(docs, scores):
                doc["score"] = float(score)
            docs = sorted(docs, key=lambda x: x["score"], reverse=True)
            logger.info(f"[SearchAgent] rerank_docs: reranked {len(docs)} docs with cross-encoder")
            return docs
        except Exception as e:
            logger.warning(f"[SearchAgent] Cross-encoder rerank failed, using keyword scoring: {e}")

    # Fallback: keyword overlap scoring
    query_terms = set(query.lower().split())
    for doc in docs:
        content_terms = set(doc["content"].lower().split())
        overlap = len(query_terms & content_terms)
        doc["score"] = doc.get("score", 0.5) + overlap * 0.01

    docs = sorted(docs, key=lambda x: x["score"], reverse=True)
    logger.info(f"[SearchAgent] rerank_docs: sorted {len(docs)} docs by keyword overlap")
    return docs


# ── Graph Nodes ────────────────────────────────────────────────────────────────

class SearchAgent:
    """
    LangGraph agent chuyên tìm kiếm.
    Được gọi bởi Supervisor khi intent = "retrieval" hoặc "web_search".
    """

    def __init__(self):
        self.graph = self._build_graph()
        logger.info("[SearchAgent] Initialized successfully.")

    # -- Nodes --

    def _dispatch_node(self, state: SearchState) -> dict:
        """Quyết định search mode và khởi tạo state"""
        logger.info(f"[SearchAgent] dispatch: mode={state['search_mode']}, query='{state['query'][:60]}'")
        return {}  # State đã được set bởi Supervisor

    def _retrieve_node(self, state: SearchState) -> dict:
        """Node: Tìm docs từ ChromaDB"""
        docs = retrieve_docs(state["query"])
        return {"retrieved_docs": docs}

    def _web_search_node(self, state: SearchState) -> dict:
        """Node: Tìm kiếm web"""
        results = google_search(state["query"])
        return {"web_results": results}

    def _hybrid_node(self, state: SearchState) -> dict:
        """Node: Kết hợp cả vector search và web search"""
        docs = retrieve_docs(state["query"])
        web = google_search(state["query"])
        return {"retrieved_docs": docs, "web_results": web}

    def _rerank_node(self, state: SearchState) -> dict:
        """Node: Rerank + tổng hợp tất cả results thành context"""
        query = state["query"]
        all_docs = []

        # Merge vector docs
        for doc in state.get("retrieved_docs", []):
            all_docs.append(doc)

        # Merge web results
        for r in state.get("web_results", []):
            all_docs.append({
                "content": r["content"],
                "document_id": r.get("url", "web"),
                "chunk_index": 0,
                "source": r.get("source", r.get("url", "web")),
                "score": r.get("score", 0.5),
                "title": r.get("title", ""),
            })

        # Rerank tất cả
        ranked = rerank_docs(all_docs, query)

        # Build context string
        context_parts = []
        selected_docs = []
        context_length = 0
        for doc in ranked:
            content = doc.get("content", "").strip()
            if not content:
                continue
            source = doc.get("source", "unknown")
            block = f"SOURCE: {source}\nCONTENT:\n{content}"
            if context_parts and context_length + len(block) > settings.MAX_CONTEXT_CHARS:
                break
            context_parts.append(block)
            selected_docs.append(doc)
            context_length += len(block)

        final_context = "\n\n---\n\n".join(context_parts)
        sources = list(dict.fromkeys(doc.get("source", "unknown") for doc in selected_docs))
        evidence_confidence = max((doc.get("score", 0.0) for doc in selected_docs), default=0.0)

        return {
            "final_context": final_context,
            "sources": sources,
            "doc_count": len(selected_docs),
            "evidence_confidence": min(max(float(evidence_confidence), 0.0), 1.0),
        }

    # -- Routing --

    def _decide_search_mode(self, state: SearchState) -> str:
        mode = state.get("search_mode", "vector")
        if mode == "web":
            return "web"
        if mode == "hybrid":
            return "hybrid"
        return "vector"  # default

    # -- Graph --

    def _build_graph(self) -> StateGraph:
        """
        START → dispatch → [retrieve | web_search | hybrid] → rerank → END
        """
        g = StateGraph(SearchState)

        g.add_node("dispatch", self._dispatch_node)
        g.add_node("retrieve", self._retrieve_node)
        g.add_node("web_search", self._web_search_node)
        g.add_node("hybrid", self._hybrid_node)
        g.add_node("rerank", self._rerank_node)

        g.set_entry_point("dispatch")

        g.add_conditional_edges(
            "dispatch",
            self._decide_search_mode,
            {
                "vector": "retrieve",
                "web": "web_search",
                "hybrid": "hybrid",
            }
        )

        g.add_edge("retrieve", "rerank")
        g.add_edge("web_search", "rerank")
        g.add_edge("hybrid", "rerank")
        g.add_edge("rerank", END)

        return g.compile()

    # -- Public API --

    def search(self, query: str, search_mode: str = "vector") -> dict:
        """
        Chạy search workflow.
        Returns: {"context": str, "sources": list, "doc_count": int}
        """
        initial_state = SearchState(
            query=query,
            search_mode=search_mode,
            retrieved_docs=[],
            web_results=[],
            final_context="",
            sources=[],
            doc_count=0,
            evidence_confidence=0.0,
        )
        result = self.graph.invoke(initial_state)
        return {
            "context": result.get("final_context", ""),
            "sources": result.get("sources", []),
            "doc_count": result.get("doc_count", 0),
            "evidence_confidence": result.get("evidence_confidence", 0.0),
        }


# Singleton
search_agent = SearchAgent()
