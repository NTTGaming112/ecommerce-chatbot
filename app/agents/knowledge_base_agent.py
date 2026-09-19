# Knowledge Base Agent
from app.tools.registry import tool_registry

def search_kb(query="", category="all"):
    r = tool_registry.execute("search_knowledge_base", {"query": query, "category": category}, agent="KnowledgeBaseAgent")
    return r.data if r.success else {"articles": [], "total_count": 0}

def _format_price(price):
    """Format price with thousand separators."""
    try:
        return f"{int(price):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(price)

def _rating_stars(rating):
    """Convert numeric rating to stars."""
    try:
        full = int(float(rating))
        return "★" * full + "☆" * (5 - full)
    except (ValueError, TypeError):
        return ""

def generate_response(message, context_results, intent):
    """Generate a natural, customer-friendly response from agent results."""
    parts = []

    # --- Extract structured data from agent results ---
    customer_name = None
    order_data = None
    products = []
    payments = []
    returns = []
    tickets = []
    troubleshooting = []
    kb_articles = []
    errors = []
    raw_info = []

    for key, val in context_results.items():
        if not isinstance(val, dict):
            continue

        if "verified" in val:
            if val["verified"]:
                customer_name = val.get("customer", {}).get("name", "you")
            else:
                errors.append(val.get("error", "We couldn't verify your identity."))

        elif "status" in val and "order_id" in val:
            order_data = val

        elif "products" in val:
            products = val.get("products", [])

        elif "articles" in val:
            kb_articles = val.get("articles", [])

        elif "payment_id" in val:
            payments.append(val)

        elif "return_id" in val or "refund_id" in val:
            returns.append(val)

        elif "ticket_id" in val:
            tickets.append(val)

        elif "troubleshooting_steps" in val:
            troubleshooting.append(val)

        elif "message" in val and "status" not in val:
            raw_info.append(val["message"])

        elif "status" in val and val.get("status") == "unknown":
            raw_info.append(val.get("message", ""))

        elif "error" in val:
            errors.append(val["error"])

    # ===================== PRODUCT QUERY =====================
    if intent == "product_query":
        if products:
            # For generic/list requests, show all
            is_list = len(products) > 1
            if is_list:
                parts.append(f"Danh sach san pham ({len(products)} san pham):")
                for i, p in enumerate(products, 1):
                    name = p.get('name', 'San pham')
                    price = _format_price(p.get('price', 0))
                    rating = p.get('rating', 0)
                    cat_labels = {'nam': 'Nam', 'nu': 'Nu', 'giay': 'Giay dep', 'phu kien': 'Phu kien', 'gia dung': 'Gia dung'}
                    cat_name = cat_labels.get(p.get('category', ''), p.get('category', ''))
                    stars = _rating_stars(rating)
                    parts.append(f"{i}. **{name}** - {price} VND")
                    parts.append(f"   {stars} ({rating}/5) | {cat_name}")
                parts.append("")
                parts.append("Nhap ten san pham de xem chi tiet, vi du: 'jacket nam', 'sneaker'")
            elif len(products) == 1:
                p = products[0]
                name = p.get("name", "San pham")
                price = _format_price(p.get("price", 0))
                rating = p.get("rating", 0)
                reviews = p.get("review_count", 0)
                cat = p.get("category", "")
                stars = _rating_stars(rating)
                cat_labels = {"nam": "Nam", "nu": "Nu", "giay": "Giay dep", "phu kien": "Phu kien", "gia dung": "Gia dung"}
                cat_name = cat_labels.get(cat, cat)
                parts.append(f"Tim thay san pham: **{name}**")
                parts.append(f"- Gia: **{price} VND**")
                parts.append(f"- Danh gia: {stars} ({rating}/5, {reviews} danh gia)")
                parts.append(f"- Phan loai: {cat_name}")
                parts.append(f"- Ma san pham: {p.get('product_id', 'N/A')}")
            else:
                parts.append(f"Tim thay **{len(products)}** san pham:\n")
                for i, p in enumerate(products, 1):
                    name = p.get("name", "San pham")
                    price = _format_price(p.get("price", 0))
                    rating = p.get("rating", 0)
                    cat_labels = {"nam": "Nam", "nu": "Nu", "giay": "Giay dep", "phu kien": "Phu kien", "gia dung": "Gia dung"}
                    cat_name = cat_labels.get(p.get("category", ""), p.get("category", ""))
                    stars = _rating_stars(rating)
                    parts.append(f"{i}. **{name}**")
                    parts.append(f"   - Gia: {price} VND | {stars} ({rating}) | {cat_name}")
        else:
            parts.append("Xin loi, toi khong tim thay san pham phu hop.")
            parts.append("Ban co the thu tim kiem voi tu khoa khac, vi du: jacket, sneaker, ao, quan...")

    # ===================== ORDER STATUS =====================
    elif intent == "order_status":
        if order_data:
            oid = order_data.get("order_id", "")
            status = order_data.get("status", "unknown")
            status_map = {
                "shipped": f"Don hang **{oid}** da duoc gui di!",
                "delivered": f"Don hang **{oid}** da duoc giao thanh cong.",
                "processing": f"Don hang **{oid}** dang duoc xu ly.",
                "pending": f"Don hang **{oid}** dang cho xac nhan.",
                "cancelled": f"Don hang **{oid}** da bi huy.",
            }
            parts.append(status_map.get(status, f"Don hang **{oid}**: {status}"))
            if order_data.get("tracking"):
                trk = order_data["tracking"]
                if isinstance(trk, dict):
                    tn = trk.get("tracking_number", "N/A")
                    carrier = trk.get("carrier", "")
                    est = trk.get("estimated_delivery", "")
                    status_icon = "Dang van chuyen" if not trk.get("is_delayed") else "Bi tre"
                    parts.append(f"- Ma theo doi: **{tn}**")
                    if carrier: parts.append(f"- Don vi van chuyen: {carrier}")
                    if est: parts.append(f"- Du kien giao hang: {est}")
                else:
                    parts.append(f"- Ma theo doi: **{trk}**")
        else:
            parts.append("Toi khong tim thay don hang phu hop.")
            for m in raw_info:
                if m: parts.append(m)

    # ===================== RETURN / REFUND =====================
    elif intent in ("refund", "return"):
        if returns:
            r = returns[0]
            parts.append(f"Yeu cau tra hang **{r.get('return_id', '')}** da duoc tao thanh cong.")
            parts.append(f"- So tien hoan: **{_format_price(r.get('refund_amount', 0))} VND**")
            parts.append(f"- Trang thai: {r.get('status', 'pending')}")
            parts.append("Ban se nhan duoc cap nhat qua email som nhat.")
        else:
            for m in raw_info:
                if m: parts.append(m)

    # ===================== BILLING =====================
    elif intent == "billing":
        if payments:
            p = payments[0]
            status_icon = "Da thanh toan" if p.get("status") == "paid" else "Chua thanh toan"
            parts.append(f"{status_icon} - Hoa don **{p.get('payment_id', '')}**")
            parts.append(f"- So tien: **{_format_price(p.get('amount', 0))} VND**")
            parts.append(f"- Phuong thuc: {p.get('payment_method', 'N/A')}")
        else:
            parts.append("Toi khong tim thay thong tin thanh toan.")
            for m in raw_info:
                if m: parts.append(m)

    # ===================== TECH SUPPORT =====================
    elif intent == "tech_support":
        if troubleshooting:
            t = troubleshooting[0]
            parts.append("Cac buoc xu ly su co:")
            for i, step in enumerate(t.get("troubleshooting_steps", [])[:4], 1):
                parts.append(f"  {i}. {step}")
        else:
            for m in raw_info:
                if m: parts.append(m)

    # ===================== HUMAN HANDOFF =====================
    elif intent == "human_handoff":
        if tickets:
            t = tickets[0]
            parts.append(f"Ve sinh ho tro **{t.get('ticket_id', '')}** da duoc tao.")
            parts.append(f"- Phu trach: {t.get('assigned_to', 'Customer Support')}")
            parts.append("Nhan vien se lien he voi ban som nhat.")
        else:
            parts.append("Dang ket noi voi nhan vien ho tro. Vui long cho...")

    # ===================== GREETING =====================
    elif intent == "greeting" and not parts:
        parts.append("Xin chao! Chao mung ban den voi **AI Customer Support**.")
        parts.append("Toi co the giup ban voi:")
        parts.append("  - Theo doi don hang va trang thai giao hang")
        parts.append("  - Tim kiem san pham va tu van")
        parts.append("  - Tra hang va hoan tien")
        parts.append("  - Van de thanh toan va hoa don")
        parts.append("  - Ho tro ky thuat")
        parts.append("Ban can giup gi hom nay?")

    # ===================== KB ARTICLES =====================
    if kb_articles:
        relevant = [a for a in kb_articles[:3] if a.get("relevance_score", 0) > 0.5]
        if relevant:
            parts.append("\nBai viet huong dan:")
            for a in relevant:
                parts.append(f"  - {a.get('title', '')}")

    # ===================== REMAINING INFO =====================
    for m in raw_info:
        if m and m not in "\n".join(parts):
            parts.append(m)

    # ===================== ERRORS =====================
    if errors and not parts:
        parts.append("Xin loi, da co loi xay ra khi xu ly yeu cau cua ban.")
        for e in errors[:2]:
            parts.append(f"- {e}")
        parts.append("Vui long thu lai hoac lien he bo phan ho tro.")

    # ===================== FALLBACK =====================
    elif not parts:
        parts.append("Toi hieu yeu cau cua ban. Vui long cung cap them thong tin de toi ho tro ban tot hon.")
        parts.append("Vi du: 'Tim jacket nam', 'Don hang ORD-12345', 'Tra hang san pham'...")

    return "\n".join(parts)
