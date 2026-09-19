# ============================================================
# Simple RAG Service - Developer Makefile
# ============================================================

.DEFAULT_GOAL := help

# ── Help (Tương thích 100% Windows, Linux, MacOS) ─────────────
.PHONY: help
help:
	@echo.
	@echo   Simple RAG Service - Cac lenh pho bien:
	@echo   ---------------------------------------
	@echo   make up           - Khoi chay toan bo he thong tren Docker
	@echo   make build        - Build lai images va khoi chay
	@echo   make down         - Dung toan bo containers
	@echo   make restart      - Khoi dong lai toan bo containers
	@echo   make logs         - Xem log thoi gian thuc cua backend
	@echo   make ps           - Xem trang thai cac containers
	@echo.
	@echo   make dev          - Chay backend cuc bo voi hot-reload (port 8000)
	@echo   make test         - Chay toan bo 25 bai kiem thu tu dong (pytest)
	@echo   make install      - Cai dat dependencies bang uv
	@echo.
	@echo   make clean-redis  - Xoa sach cache du lieu trong Redis
	@echo   make sync-kb      - Dong bo KB tu SQLite sang ChromaDB
	@echo   make clean        - Dung containers va xoa sach data volumes
	@echo.

# ── Docker Commands (Phổ biến) ──────────────────────────────
.PHONY: up
up:
	docker compose up -d

.PHONY: build
build:
	docker compose up --build -d

.PHONY: down
down:
	docker compose down

.PHONY: restart
restart:
	docker compose restart

.PHONY: logs
logs:
	docker compose logs -f backend

.PHONY: ps
ps:
	docker compose ps

# ── Local Development & Testing ─────────────────────────────
.PHONY: dev
dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: test
test:
	uv run pytest

.PHONY: install
install:
	uv sync

# ── Data & Maintenance ──────────────────────────────────────
.PHONY: clean-redis
clean-redis:
	docker exec rag_redis redis-cli FLUSHALL

.PHONY: sync-kb
sync-kb:
	uv run python -c "from app.services.retrieval_service import retrieval_service; print(retrieval_service.sync_kb_from_db())"

.PHONY: clean
clean:
	docker compose down -v
