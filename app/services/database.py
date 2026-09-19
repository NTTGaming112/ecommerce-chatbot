"""Database Service - SQLite storage for StyleHub E-commerce Multi-Agent System.

Manages Relational Data (Single Source of Truth):
1. Knowledge Base: Policies, Regulations, Guides, FAQ (`kb_articles`)
2. E-commerce Domain Data: Customers, Products, Orders, Shipping, Payments, Returns, Tickets, Troubleshooting
"""

import glob
import json
import logging
import os
import re
import sqlite3
import unicodedata
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "ecommerce.db")
KB_DIR = os.path.join(BASE_DIR, "kb")


def _normalize_vn(text: str) -> str:
    """Remove diacritics from Vietnamese string for fuzzy search."""
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    ).lower()


class DatabaseService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """Create tables if not exists and seed initial data if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # ─── 1. KNOWLEDGE BASE (Chính sách, Quy định, Hướng dẫn, FAQ) ───────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS kb_articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                slug TEXT UNIQUE,
                content TEXT NOT NULL,
                tags TEXT,
                file_path TEXT,
                updated_at TEXT
            )""")

            # ─── 2. DOMAIN DATA: CUSTOMERS ─────────────────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                loyalty_tier TEXT,
                total_spent INTEGER DEFAULT 0,
                created_at TEXT
            )""")

            # ─── 3. DOMAIN DATA: PRODUCTS ──────────────────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                original_price INTEGER,
                category TEXT,
                rating REAL,
                review_count INTEGER,
                description TEXT,
                colors TEXT,
                sizes TEXT,
                tags TEXT,
                stock_info TEXT,
                in_stock INTEGER DEFAULT 1
            )""")

            # ─── 4. DOMAIN DATA: ORDERS ────────────────────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                status TEXT NOT NULL,
                items TEXT NOT NULL,
                total INTEGER NOT NULL,
                shipping_fee INTEGER DEFAULT 0,
                payment_method TEXT,
                shipping_address TEXT,
                tracking_number TEXT,
                carrier TEXT,
                created_at TEXT,
                delivered_at TEXT,
                cancelled_at TEXT,
                cancel_reason TEXT
            )""")

            # ─── 5. DOMAIN DATA: SHIPPING ──────────────────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipping (
                tracking_number TEXT PRIMARY KEY,
                carrier TEXT,
                current_status TEXT,
                estimated_delivery TEXT,
                is_delayed INTEGER DEFAULT 0,
                delay_reason TEXT,
                delivered_at TEXT,
                checkpoints TEXT
            )""")

            # ─── 6. DOMAIN DATA: PAYMENTS ──────────────────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                order_id TEXT,
                customer_id TEXT,
                status TEXT,
                amount INTEGER,
                method TEXT,
                paid_at TEXT
            )""")

            # ─── 7. DOMAIN DATA: RETURNS ───────────────────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                return_id TEXT PRIMARY KEY,
                order_id TEXT,
                customer_id TEXT,
                status TEXT,
                refund_amount INTEGER,
                estimated_refund_date TEXT,
                instructions TEXT,
                reason TEXT,
                created_at TEXT
            )""")

            # ─── 8. DOMAIN DATA: SUPPORT TICKETS ───────────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_id TEXT,
                category TEXT,
                priority TEXT,
                status TEXT,
                subject TEXT,
                created_at TEXT
            )""")

            # ─── 9. DOMAIN DATA: TROUBLESHOOTING GUIDES ────────────────────────
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS troubleshooting (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_key TEXT,
                product_name TEXT,
                symptom TEXT,
                solutions TEXT
            )""")

            # Check if seeding is needed for Domain tables
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] == 0:
                logger.info("Database is empty. Seeding domain data...")
                self._seed_data(cursor)

            # Check if seeding is needed for KB articles
            cursor.execute("SELECT COUNT(*) FROM kb_articles")
            if cursor.fetchone()[0] == 0:
                logger.info("Seeding KB articles (Policies, Guides, FAQ)...")
                self._seed_kb_articles(cursor)

    def _seed_kb_articles(self, cursor):
        """Seed KB articles from markdown files (policy, guides, faq) and mock data."""
        # 1. Quét các file markdown trong kb/
        category_map = {
            "policy": "policy",
            "guides": "guide",
            "faq": "faq",
        }
        for folder_name, cat in category_map.items():
            folder_path = os.path.join(KB_DIR, folder_name)
            if not os.path.exists(folder_path):
                continue
            for file_path in glob.glob(os.path.join(folder_path, "*.md")):
                slug = os.path.splitext(os.path.basename(file_path))[0]
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    logger.warning("Could not read KB file %s: %s", file_path, e)
                    continue

                # Trích xuất tiêu đề từ dòng # đầu tiên
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()

                article_id = f"KB-{cat.upper()}-{slug}"
                tags = [cat, slug.replace("-", " ")]
                cursor.execute(
                    """INSERT OR REPLACE INTO kb_articles
                       (article_id, title, category, slug, content, tags, file_path, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                    (article_id, title, cat, slug, content, json.dumps(tags, ensure_ascii=False), file_path)
                )

        # 2. Bổ sung từ MOCK_KB_ARTICLES (KB-001..KB-012) để tương thích test cũ
        from app.tools.mock_data import MOCK_KB_ARTICLES
        for art in MOCK_KB_ARTICLES:
            cursor.execute(
                """INSERT OR REPLACE INTO kb_articles
                   (article_id, title, category, slug, content, tags, file_path, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (
                    art["id"], art["title"], art["category"],
                    art["id"].lower(), art["content"],
                    json.dumps(art.get("tags", []), ensure_ascii=False),
                    f"kb/{art['category']}/{art['id'].lower()}.md"
                )
            )

        logger.info("KB articles seeded into SQLite successfully.")

    def _seed_data(self, cursor):
        """Seed domain tables from app.tools.mock_data."""
        from app.tools.mock_data import (
            MOCK_CUSTOMERS, MOCK_PRODUCTS, MOCK_ORDERS, MOCK_SHIPPING,
            MOCK_PAYMENTS, MOCK_STOCK, TROUBLESHOOTING_GUIDES,
        )

        for cid, c in MOCK_CUSTOMERS.items():
            cursor.execute(
                """INSERT OR REPLACE INTO customers 
                   (customer_id, name, email, phone, address, loyalty_tier, total_spent, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    c["customer_id"], c["name"], c.get("email"), c.get("phone"),
                    json.dumps(c.get("address", {}), ensure_ascii=False),
                    c.get("loyalty_tier"), c.get("total_spent", 0), c.get("created_at")
                )
            )

        for p in MOCK_PRODUCTS:
            pid = p["product_id"]
            stock = MOCK_STOCK.get(pid, {})
            cursor.execute(
                """INSERT OR REPLACE INTO products
                   (product_id, name, price, original_price, category, rating, review_count, 
                    description, colors, sizes, tags, stock_info, in_stock)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pid, p["name"], p["price"], p.get("original_price"),
                    p.get("category"), p.get("rating", 5.0), p.get("review_count", 0),
                    p.get("description", ""),
                    json.dumps(p.get("colors", []), ensure_ascii=False),
                    json.dumps(p.get("sizes", []), ensure_ascii=False),
                    json.dumps(p.get("tags", []), ensure_ascii=False),
                    json.dumps(stock, ensure_ascii=False),
                    1 if stock.get("in_stock", True) else 0
                )
            )

        for oid, o in MOCK_ORDERS.items():
            cursor.execute(
                """INSERT OR REPLACE INTO orders
                   (order_id, customer_id, status, items, total, shipping_fee, payment_method,
                    shipping_address, tracking_number, carrier, created_at, delivered_at, cancelled_at, cancel_reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    o["order_id"], o["customer_id"], o["status"],
                    json.dumps(o.get("items", []), ensure_ascii=False),
                    o.get("total", 0), o.get("shipping_fee", 0), o.get("payment_method"),
                    json.dumps(o.get("shipping_address", {}), ensure_ascii=False),
                    o.get("tracking_number"), o.get("carrier"),
                    o.get("created_at"), o.get("delivered_at"), o.get("cancelled_at"), o.get("cancel_reason")
                )
            )

        for trk, s in MOCK_SHIPPING.items():
            cursor.execute(
                """INSERT OR REPLACE INTO shipping
                   (tracking_number, carrier, current_status, estimated_delivery, is_delayed,
                    delay_reason, delivered_at, checkpoints)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    s["tracking_number"], s.get("carrier"), s.get("current_status"),
                    s.get("estimated_delivery"), 1 if s.get("is_delayed") else 0,
                    s.get("delay_reason"), s.get("delivered_at"),
                    json.dumps(s.get("checkpoints", []), ensure_ascii=False)
                )
            )

        for key, p in MOCK_PAYMENTS.items():
            cursor.execute(
                """INSERT OR REPLACE INTO payments
                   (payment_id, order_id, customer_id, status, amount, method, paid_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    p.get("payment_id", f"PAY-{key}"), p.get("order_id", key),
                    p.get("customer_id"), p.get("status"), p.get("amount", 0),
                    p.get("method"), p.get("paid_at")
                )
            )

        for pkey, info in TROUBLESHOOTING_GUIDES.items():
            pname = info.get("product", "")
            for symptom, solutions in info.get("symptoms", {}).items():
                cursor.execute(
                    """INSERT INTO troubleshooting (product_key, product_name, symptom, solutions)
                       VALUES (?, ?, ?, ?)""",
                    (pkey, pname, symptom, json.dumps(solutions, ensure_ascii=False))
                )

        logger.info("Ecommerce database seeded successfully.")

    # ─── KB ARTICLES CRUD (Relational DB) ─────────────────────────────────────
    def get_kb_article(self, article_id_or_slug: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM kb_articles WHERE article_id = ? OR slug = ?",
                (article_id_or_slug, article_id_or_slug)
            )
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["tags"] = json.loads(data["tags"]) if data.get("tags") else []
            return data

    def get_all_kb_articles(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM kb_articles WHERE category = ? ORDER BY article_id", (category,))
            else:
                cursor.execute("SELECT * FROM kb_articles ORDER BY category, article_id")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                data = dict(r)
                data["tags"] = json.loads(data["tags"]) if data.get("tags") else []
                results.append(data)
            return results

    def search_kb_articles(self, query: str = "", category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Exact and normalized fuzzy SQL search for policies, guides, regulations, and FAQs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kb_articles")
            rows = cursor.fetchall()

            q_clean = query.strip()
            q_norm = _normalize_vn(q_clean)
            results = []
            for row in rows:
                data = dict(row)
                data["id"] = data.get("article_id")
                data["tags"] = json.loads(data["tags"]) if data.get("tags") else []

                if category and category != "all" and data.get("category", "").lower() != category.lower():
                    continue

                if not q_clean:
                    results.append(data)
                    continue

                title_norm = _normalize_vn(data["title"])
                content_norm = _normalize_vn(data["content"])
                tags_norm = " ".join(_normalize_vn(t) for t in data["tags"])

                if (q_norm in title_norm or 
                    q_norm in content_norm or 
                    q_norm in tags_norm or 
                    any(part in title_norm or part in tags_norm for part in q_norm.split() if len(part) > 2)):
                    results.append(data)

            return results[:limit]

    def save_kb_article(self, article_id: str, title: str, category: str,
                        content: str, tags: List[str], slug: Optional[str] = None,
                        file_path: Optional[str] = None) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            actual_slug = slug or article_id.lower()
            cursor.execute(
                """INSERT OR REPLACE INTO kb_articles
                   (article_id, title, category, slug, content, tags, file_path, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (article_id, title, category, actual_slug, content, json.dumps(tags, ensure_ascii=False), file_path)
            )
            return self.get_kb_article(article_id)

    # ─── CUSTOMER CRUD ────────────────────────────────────────────────────────
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["address"] = json.loads(data["address"]) if data.get("address") else {}
            return data

    def get_all_customers(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers ORDER BY customer_id")
            rows = cursor.fetchall()
            results = []
            for row in rows:
                data = dict(row)
                data["address"] = json.loads(data["address"]) if data.get("address") else {}
                results.append(data)
            return results

    # ─── ORDER CRUD ───────────────────────────────────────────────────────────
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["items"] = json.loads(data["items"]) if data.get("items") else []
            data["shipping_address"] = json.loads(data["shipping_address"]) if data.get("shipping_address") else {}
            return data

    def get_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                data = dict(row)
                data["items"] = json.loads(data["items"]) if data.get("items") else []
                data["shipping_address"] = json.loads(data["shipping_address"]) if data.get("shipping_address") else {}
                results.append(data)
            return results

    def cancel_order(self, order_id: str, reason: str = "Khách yêu cầu hủy") -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cursor.execute(
                """UPDATE orders 
                   SET status = 'cancelled', cancel_reason = ?, cancelled_at = datetime('now')
                   WHERE order_id = ?""",
                (reason, order_id)
            )
            return self.get_order(order_id)

    def update_order_address(self, order_id: str, new_address: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE orders 
                   SET shipping_address = ?
                   WHERE order_id = ?""",
                (json.dumps(new_address, ensure_ascii=False), order_id)
            )
            return self.get_order(order_id)

    # ─── SHIPPING CRUD ────────────────────────────────────────────────────────
    def get_shipping(self, tracking_number: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shipping WHERE tracking_number = ?", (tracking_number,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["is_delayed"] = bool(data.get("is_delayed"))
            data["checkpoints"] = json.loads(data["checkpoints"]) if data.get("checkpoints") else []
            return data

    # ─── PRODUCT CRUD ─────────────────────────────────────────────────────────
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["colors"] = json.loads(data["colors"]) if data.get("colors") else []
            data["sizes"] = json.loads(data["sizes"]) if data.get("sizes") else []
            data["tags"] = json.loads(data["tags"]) if data.get("tags") else []
            data["stock_info"] = json.loads(data["stock_info"]) if data.get("stock_info") else {}
            data["in_stock"] = bool(data.get("in_stock"))
            return data

    def search_products(self, query: str = "", category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search products with diacritics normalization & category filtering."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()

            q_clean = query.strip()
            q_norm = _normalize_vn(q_clean)

            results = []
            for row in rows:
                data = dict(row)
                data["colors"] = json.loads(data["colors"]) if data.get("colors") else []
                data["sizes"] = json.loads(data["sizes"]) if data.get("sizes") else []
                data["tags"] = json.loads(data["tags"]) if data.get("tags") else []
                data["stock_info"] = json.loads(data["stock_info"]) if data.get("stock_info") else {}
                data["in_stock"] = bool(data.get("in_stock"))

                if category and category.lower() != data.get("category", "").lower():
                    continue

                if not q_clean:
                    results.append(data)
                    continue

                name_norm = _normalize_vn(data["name"])
                tags_norm = " ".join(_normalize_vn(t) for t in data["tags"])
                desc_norm = _normalize_vn(data.get("description", ""))

                if (q_norm in name_norm or 
                    q_norm in tags_norm or 
                    q_norm in desc_norm or 
                    any(part in name_norm or part in tags_norm for part in q_norm.split() if len(part) > 2)):
                    results.append(data)

            return results[:limit]

    # ─── PAYMENT CRUD ─────────────────────────────────────────────────────────
    def get_payment_by_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ─── RETURNS & REFUNDS ───────────────────────────────────────────────────
    def create_return(self, order_id: str, customer_id: str, refund_amount: int,
                      instructions: str, reason: str = "") -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM returns")
            next_id = f"RET-{100 + cursor.fetchone()[0] + 1}"
            status = "pending_approval" if refund_amount > 500 * 1000 else "approved"
            cursor.execute(
                """INSERT INTO returns
                   (return_id, order_id, customer_id, status, refund_amount, estimated_refund_date, instructions, reason, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (next_id, order_id, customer_id, status, refund_amount, "2026-09-01", instructions, reason)
            )
            return {
                "return_id": next_id,
                "status": status,
                "refund_amount": refund_amount,
                "estimated_refund_date": "2026-09-01",
                "instructions": instructions,
            }

    # ─── SUPPORT TICKETS ──────────────────────────────────────────────────────
    def create_ticket(self, customer_id: str, subject: str, priority: str = "medium", category: str = "general") -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tickets")
            next_id = f"TKT-{500 + cursor.fetchone()[0] + 1}"
            cursor.execute(
                """INSERT INTO tickets (ticket_id, customer_id, category, priority, status, subject, created_at)
                   VALUES (?, ?, ?, ?, 'open', ?, datetime('now'))""",
                (next_id, customer_id, category, priority, subject)
            )
            return {
                "ticket_id": next_id,
                "status": "open",
                "priority": priority,
                "subject": subject,
            }

    # ─── TROUBLESHOOTING ──────────────────────────────────────────────────────
    def get_troubleshooting_guides(self, product_key: str, symptom: str = "") -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if symptom:
                cursor.execute(
                    "SELECT solutions FROM troubleshooting WHERE product_key = ? AND symptom LIKE ?",
                    (product_key, f"%{symptom}%")
                )
            else:
                cursor.execute(
                    "SELECT solutions FROM troubleshooting WHERE product_key = ?",
                    (product_key,)
                )
            rows = cursor.fetchall()
            solutions = []
            for r in rows:
                s_list = json.loads(r["solutions"]) if r["solutions"] else []
                solutions.extend(s_list)
            return solutions

    def get_all_troubleshooting(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM troubleshooting ORDER BY product_key")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                data = dict(r)
                data["solutions"] = json.loads(data["solutions"]) if data.get("solutions") else []
                results.append(data)
            return results


# Global database instance
db_service = DatabaseService()
