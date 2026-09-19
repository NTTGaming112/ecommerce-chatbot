# ============================================================
# Simple RAG Service - Makefile
# ============================================================

.DEFAULT_GOAL := help

# ── Variables ────────────────────────────────────────────────
COMPOSE = docker-compose
BACKEND = simple_rag_service-backend-1
FRONTEND = simple_rag_service-frontend-1

# ── Help ─────────────────────────────────────────────────────
.PHONY: help
help: ## Hiển thị tất cả lệnh
	@echo ""
	@echo "  Simple RAG Service - Makefile Commands"
	@echo "  ======================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ── Build & Run ───────────────────────────────────────────────
.PHONY: up
up: ## Khởi chạy toàn bộ services (backend + frontend + redis)
	$(COMPOSE) up -d

.PHONY: build
build: ## Build lại image và khởi chạy
	$(COMPOSE) up --build -d

.PHONY: down
down: ## Dừng tất cả services
	$(COMPOSE) down

.PHONY: restart
restart: ## Restart tất cả services
	$(COMPOSE) restart

.PHONY: restart-backend
restart-backend: ## Restart chỉ backend (áp dụng thay đổi code nhanh)
	$(COMPOSE) restart backend

.PHONY: rebuild-backend
rebuild-backend: ## Rebuild và restart chỉ backend
	$(COMPOSE) up --build -d backend

# ── Logs ─────────────────────────────────────────────────────
.PHONY: logs
logs: ## Xem log tất cả services (Ctrl+C để thoát)
	$(COMPOSE) logs -f

.PHONY: logs-backend
logs-backend: ## Xem log backend
	$(COMPOSE) logs -f backend

.PHONY: logs-frontend
logs-frontend: ## Xem log frontend
	$(COMPOSE) logs -f frontend

.PHONY: logs-redis
logs-redis: ## Xem log Redis
	$(COMPOSE) logs -f redis

# ── Health & Status ───────────────────────────────────────────
.PHONY: ps
ps: ## Xem trạng thái các containers
	$(COMPOSE) ps

.PHONY: health
health: ## Kiểm tra health của backend API
	@curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || \
		echo "Backend chưa sẵn sàng. Chạy 'make up' trước."

.PHONY: status
status: ps health ## Xem trạng thái đầy đủ

# ── Testing ───────────────────────────────────────────────────
.PHONY: test
test: ## Chạy regression tests
	@uv run pytest -q

.PHONY: test-health
test-health: ## Test health endpoint
	@curl -s http://localhost:8000/health

.PHONY: test-ingest
test-ingest: ## Test ingest một đoạn text mẫu
	@curl -s -X POST http://localhost:8000/api/v1/ingest \
		-H "Content-Type: application/json" \
		-d '{"document_id":"test_doc","text_content":"Đây là tài liệu test. Công ty ABC chuyên cung cấp giải pháp AI."}' \
		| python -m json.tool

.PHONY: test-ask
test-ask: ## Test hỏi đáp với AI
	@curl -s -X POST http://localhost:8000/api/v1/ask \
		-H "Content-Type: application/json" \
		-d '{"session_id":"test123","question":"Xin chào, bạn là ai?"}' \
		| python -m json.tool

# ── Shell Access ──────────────────────────────────────────────
.PHONY: shell-backend
shell-backend: ## Mở shell trong backend container
	docker exec -it $(BACKEND) /bin/bash

.PHONY: redis-cli
redis-cli: ## Mở Redis CLI
	docker exec -it simple_rag_service-redis-1 redis-cli

# ── Docs ──────────────────────────────────────────────────────
.PHONY: docs
docs: ## Mở Swagger API docs trên browser
	@start http://localhost:8000/docs 2>/dev/null || \
		open http://localhost:8000/docs 2>/dev/null || \
		echo "Mở trình duyệt và truy cập: http://localhost:8000/docs"

.PHONY: frontend
frontend: ## Mở Frontend trên browser
	@start http://localhost:3000 2>/dev/null || \
		open http://localhost:3000 2>/dev/null || \
		echo "Mở trình duyệt và truy cập: http://localhost:3000"

# ── Cleanup ───────────────────────────────────────────────────
.PHONY: clean
clean: ## Dừng và xóa containers (giữ lại data volumes)
	$(COMPOSE) down

.PHONY: clean-all
clean-all: ## Dừng và xóa containers + volumes (XÓA HẾT DATA)
	$(COMPOSE) down -v
	@rm -rf chroma_data/ data/
	@echo "Đã xóa toàn bộ data!"

.PHONY: clean-cache
clean-cache: ## Xóa Docker build cache
	docker builder prune -f

# ── Dev Mode (local, không dùng Docker) ──────────────────────
.PHONY: infra-up
infra-up: ## Khởi chạy chỉ Redis (chạy backend local)
	$(COMPOSE) up -d redis

.PHONY: run-local
run-local: ## Chạy backend local (uv tự quản lý venv)
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: install-deps
install-deps: ## Cài đặt Python dependencies và tạo/cập nhật uv.lock
	uv sync

.PHONY: lock
lock: ## Resolve dependencies và cập nhật uv.lock (không install)
	uv lock

.PHONY: lock-upgrade
lock-upgrade: ## Upgrade tất cả packages lên phiên bản mới nhất
	uv lock --upgrade

# ── Knowledge Base ────────────────────────────────────────────
.PHONY: seed-kb
seed-kb: ## Nạp tài liệu trong kb/ vào ChromaDB (bỏ qua doc đã có)
	uv run python scripts/seed_kb.py

.PHONY: seed-kb-reset
seed-kb-reset: ## Xóa collection và nạp lại toàn bộ tài liệu
	uv run python scripts/seed_kb.py --reset
