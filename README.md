# Simple RAG Service

AI Customer Support multi-agent system: FastAPI + LangGraph agents + ChromaDB + Redis.

## Structure

- `app/main.py` — FastAPI app, WebSocket chat, router mounting
- `app/api/routers/` — REST endpoints (`/api/v1/chat`, `/api/v1/ask`, `/api/v1/ingest`, `/api/v1/health`, `/api/v1/tools`)
- `app/agents/` — Orchestrator + domain agents (order, refund, billing, tech support, ...)
- `app/services/` — Supervisor pipeline (LLM), retrieval (ChromaDB), memory (Redis + SQLite)
- `app/tools/` — Tool registry with read/write tools and mock data
- `frontend/` — React + Vite chat UI
- `tests/` — pytest suite (workflows, memory, policy, prompts, schemas)

## Quick start

```bash
# with Docker
make up

# local dev
make infra-up     # start Redis
make run-local    # uvicorn with reload on :8000
```

API docs: <http://localhost:8000/docs> · Chat UI: <http://localhost:8000/chat>

## Testing

```bash
make test    # uv run pytest -q
```

## Configuration

Copy `.env` values or set env vars — see `app/core/config.py` (`GOOGLE_API_KEY`, `REDIS_HOST`, `CHROMA_PERSIST_DIR`, ...).
