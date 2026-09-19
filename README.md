# Simple RAG Service

Hệ thống AI Customer Support Multi-Agent kết hợp **Relational DB** (SQLite) và **Vector DB** (ChromaDB RAG).

## 🚀 Khởi chạy nhanh (Docker)

```bash
# 1. Cấu hình biến môi trường
cp .env.example .env    # Hoặc điền GOOGLE_API_KEY vào .env

# 2. Khởi chạy toàn bộ hệ thống (Backend, Frontend, Redis)
make up
```

- **Frontend Web UI**: <http://localhost:3000>
- **Backend API Docs**: <http://localhost:8000/docs>

## 🛠️ Lệnh phổ biến (`Makefile`)

| Lệnh | Chức năng |
| :--- | :--- |
| `make up` | Khởi chạy hệ thống trên Docker (chạy ngầm) |
| `make down` | Dừng toàn bộ containers |
| `make build` | Build lại toàn bộ images và khởi chạy |
| `make logs` | Xem logs thời gian thực của backend |
| `make test` | Chạy bộ kiểm thử tự động (`pytest`) |
| `make dev` | Chạy backend cục bộ với hot-reload (`:8000`) |
| `make sync-kb` | Đồng bộ Knowledge Base từ SQLite sang ChromaDB |
| `make clean-redis` | Xóa sạch cache hội thoại trong Redis |

## 🏗️ Cấu trúc hệ thống

- `app/api/routers/` — REST endpoints (`chat`, `ecommerce`, `ingest`, `health`)
- `app/services/` — 
  - `database.py`: SQLite Relational DB (Khách hàng, Sản phẩm, Đơn hàng, Vận chuyển, Đổi trả)
  - `retrieval_service.py`: ChromaDB Vector DB cho Knowledge Base
  - `confirmation_service.py`: Luồng xác nhận tương tác cho hành động hủy đơn/trả hàng
  - `llm_service.py` & `answer_agent.py`: Trả lời tự nhiên, grounding từ dữ liệu thực tế
- `app/agents/` — Domain fetcher, phân loại ý định (router), hỗ trợ kỹ thuật
- `frontend/` — Giao diện React + Tailwind CSS (5 tabs: Trợ lý AI, Đơn hàng, Sản phẩm, KB, Kỹ thuật)
- `kb/` — Tài liệu Knowledge Base (Chính sách, Hướng dẫn, FAQ)
- `tests/` — Bộ kiểm thử tự động toàn diện (`test_workflows.py`)
