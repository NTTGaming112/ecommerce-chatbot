# Knowledge Base

Tài liệu nội bộ dùng làm nguồn retrieval cho RAG (ChromaDB, collection `support_docs`).

```
kb/
├── policy/     # Chính sách: đổi trả, hoàn tiền, vận chuyển, bảo hành
├── products/   # Thông tin sản phẩm + xử lý sự cố
├── guides/     # Hướng dẫn quy trình
└── faq/        # Câu hỏi thường gặp
```

## Cách nạp vào vector store

```bash
make seed-kb          # nạp tài liệu mới (bỏ qua doc đã ingested)
make seed-kb-reset    # xóa collection, nạp lại toàn bộ
```

Chạy trực tiếp: `uv run python scripts/seed_kb.py [--reset]`

Mỗi file `.md` là một document với `document_id` = đường dẫn tương đối (ví dụ `policy/doi-tra-hang.md`), được chia chunk 500 ký tự trước khi nhúng. Script idempotent — chạy lại không bị trùng dữ liệu.

Để thêm tài liệu mới: tạo file `.md` trong thư mục con phù hợp rồi chạy lại `make seed-kb`.
