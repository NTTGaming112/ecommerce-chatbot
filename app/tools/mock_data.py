"""Mock Data for development mode"""

MOCK_CUSTOMERS = {
    "cust_001": {"customer_id": "cust_001", "name": "Nguyen Van An", "email": "nguyenvana@email.com", "phone": "0901234567", "address": {"street": "123", "city": "HCM"}, "loyalty_tier": "gold", "created_at": "2024-01-15T00:00:00Z"},
    "cust_002": {"customer_id": "cust_002", "name": "Tran Thi Binh", "email": "tranthib@email.com", "phone": "0912345678", "address": {"street": "123", "city": "HN"}, "loyalty_tier": "silver", "created_at": "2024-01-15T00:00:00Z"},
    "cust_003": {"customer_id": "cust_003", "name": "Le Minh Canh", "email": "leminhc@email.com", "phone": "0923456789", "address": {"street": "123", "city": "DN"}, "loyalty_tier": "platinum", "created_at": "2024-01-15T00:00:00Z"},
    "cust_004": {"customer_id": "cust_004", "name": "Pham Thu Dung", "email": "phamthud@email.com", "phone": "0934567890", "address": {"street": "123", "city": "HP"}, "loyalty_tier": "bronze", "created_at": "2024-01-15T00:00:00Z"},
    "cust_005": {"customer_id": "cust_005", "name": "Hoang Duc Em", "email": "hoangdue@email.com", "phone": "0945678901", "address": {"street": "123", "city": "CT"}, "loyalty_tier": "gold", "created_at": "2024-01-15T00:00:00Z"},
}

MOCK_PRODUCTS = [
    {"product_id": "prod_001", "name": "Ao Jacket Nam Xanh", "price": 590000, "category": "nam", "rating": 4.5, "review_count": 100},
    {"product_id": "prod_002", "name": "Quan Jean Nam", "price": 350000, "category": "nam", "rating": 4.5, "review_count": 100},
    {"product_id": "prod_003", "name": "Ao So Mi Nu Trang", "price": 420000, "category": "nu", "rating": 4.5, "review_count": 100},
    {"product_id": "prod_004", "name": "Vay Dam Da Hoi", "price": 1200000, "category": "nu", "rating": 4.5, "review_count": 100},
    {"product_id": "prod_005", "name": "Giay Sneaker Nam", "price": 890000, "category": "giay", "rating": 4.5, "review_count": 100},
    {"product_id": "prod_006", "name": "May Loc Nuoc XYZ", "price": 2500000, "category": "gia dung", "rating": 4.5, "review_count": 100},
    {"product_id": "prod_007", "name": "Tui Xach Nu Da That", "price": 1800000, "category": "phu kien", "rating": 4.5, "review_count": 100},
    {"product_id": "prod_008", "name": "Dong Ho Nam The Thao", "price": 1500000, "category": "phu kien", "rating": 4.5, "review_count": 100},
]
MOCK_PRODUCTS_BY_ID = {p["product_id"]: p for p in MOCK_PRODUCTS}

MOCK_STOCK = {
    "prod_001": {"in_stock": True, "variants": [{"color": "Xanh", "size": "M", "quantity": 15, "available": True}, {"color": "Den", "size": "L", "quantity": 12, "available": True}]},
    "prod_003": {"in_stock": True, "variants": [{"color": "Trang", "size": "S", "quantity": 30, "available": True}], "restock_date": "2026-09-01"},
    "prod_006": {"in_stock": False, "variants": [], "restock_date": "2026-09-15"},
}

MOCK_ORDERS = {
    "ORD-12345": {"order_id": "ORD-12345", "customer_id": "cust_001", "status": "shipped", "items": [{"name": "Ao Jacket", "qty": 1, "price": 590000}], "total": 590000, "created_at": "2026-08-21T10:00:00Z", "tracking_number": "TRK-789", "carrier": "GHN"},
    "ORD-12346": {"order_id": "ORD-12346", "customer_id": "cust_001", "status": "delivered", "items": [{"name": "Quan Jean", "qty": 1, "price": 350000}], "total": 700000, "created_at": "2026-08-21T10:00:00Z", "tracking_number": "TRK-890", "carrier": "Viettel Post"},
    "ORD-12347": {"order_id": "ORD-12347", "customer_id": "cust_001", "status": "processing", "items": [{"name": "Giay Sneaker", "qty": 1, "price": 890000}], "total": 890000, "created_at": "2026-08-21T10:00:00Z"},
    "ORD-20001": {"order_id": "ORD-20001", "customer_id": "cust_002", "status": "processing", "items": [{"name": "Ao So Mi", "qty": 1, "price": 420000}], "total": 420000, "created_at": "2026-08-21T10:00:00Z"},
    "ORD-20002": {"order_id": "ORD-20002", "customer_id": "cust_002", "status": "pending", "items": [{"name": "Vay Dam", "qty": 1, "price": 1200000}], "total": 1200000, "created_at": "2026-08-21T10:00:00Z"},
    "ORD-30001": {"order_id": "ORD-30001", "customer_id": "cust_003", "status": "cancelled", "items": [{"name": "Giay Sneaker", "qty": 1, "price": 890000}], "total": 890000, "created_at": "2026-08-21T10:00:00Z"},
    "ORD-30002": {"order_id": "ORD-30002", "customer_id": "cust_003", "status": "delivered", "items": [{"name": "Tui Xach", "qty": 1, "price": 1800000}], "total": 1800000, "created_at": "2026-08-21T10:00:00Z", "tracking_number": "TRK-111", "carrier": "GHN"},
}

MOCK_SHIPPING = {
    "TRK-789": {"tracking_number": "TRK-789", "carrier": "GHN", "current_status": "in_transit", "estimated_delivery": "2026-08-27", "is_delayed": False},
    "TRK-890": {"tracking_number": "TRK-890", "carrier": "Viettel Post", "current_status": "delivered", "estimated_delivery": "2026-08-12", "is_delayed": False},
    "TRK-111": {"tracking_number": "TRK-111", "carrier": "GHN", "current_status": "delivered", "estimated_delivery": "2026-08-08", "is_delayed": False},
}

MOCK_PAYMENTS = {
    "ORD-12345": {"payment_id": "PAY-001", "order_id": "ORD-12345", "customer_id": "cust_001", "status": "completed", "amount": 590000, "method": "Visa ****4242"},
    "ORD-12346": {"payment_id": "PAY-002", "order_id": "ORD-12346", "customer_id": "cust_001", "status": "completed", "amount": 700000, "method": "MoMo"},
    "ORD-20002": {"payment_id": "PAY-003", "order_id": "ORD-20002", "customer_id": "cust_002", "status": "failed", "amount": 1200000, "method": "VNPay", "failure_reason": "Insufficient funds"},
    "ORD-30002": {"payment_id": "PAY-004", "order_id": "ORD-30002", "customer_id": "cust_003", "status": "completed", "amount": 1800000, "method": "Visa ****1234"},
}

MOCK_INVOICES = {
    "ORD-12345": {"invoice_id": "INV-001", "total": 590000, "status": "paid"},
    "ORD-30002": {"invoice_id": "INV-003", "total": 1800000, "status": "paid"},
}

MOCK_KB_ARTICLES = [
    {"id": "KB-001", "title": "Chinh sach doi tra", "category": "policy", "content": "Doi/tra trong 30 ngay. Con tem, chua su dung."},
    {"id": "KB-002", "title": "Chinh sach hoan tien", "category": "policy", "content": "Hoan ve phuong thuc goc 5-7 ngay."},
    {"id": "KB-003", "title": "Theo doi don hang", "category": "guide", "content": "Cung cap ma don/van don. Giao 2-5 ngay."},
    {"id": "KB-004", "title": "May loc nuoc - Xu ly su co", "category": "guide", "content": "Den do: 1) Kiem tra nguon dien, 2) Thay loi loc, 3) Kiem tra van."},
    {"id": "KB-005", "title": "Phuong thuc thanh toan", "category": "faq", "content": "Visa/MC, VNPay, MoMo, ZaloPay, COD."},
    {"id": "KB-006", "title": "Chinh sach van chuyen", "category": "policy", "content": "Mien ship >500K. Phi: 30K noi thanh."},
    {"id": "KB-007", "title": "Thanh toan tru 2 lan", "category": "faq", "content": "Cung cap ma GD + sao ke. Hoan 3-5 ngay."},
    {"id": "KB-008", "title": "Bao hanh", "category": "policy", "content": "Dien tu: 12 thang. Thoi trang: 30 ngay."},
    {"id": "KB-009", "title": "Huy don hang", "category": "faq", "content": "Lien he 24h. Chi huy khi pending/confirmed."},
    {"id": "KB-010", "title": "Uu dai VIP", "category": "faq", "content": "Gold: -5%. Platinum: -10%. Silver: -3%."},
]
MOCK_KB_BY_ID = {a["id"]: a for a in MOCK_KB_ARTICLES}

RETURN_POLICY = {"return_window_days": 30, "refund_timeline": "5-7 ngay", "high_value_threshold": 500}

TROUBLESHOOTING_GUIDES = {
    "may_loc_nuoc": {"product": "May Loc Nuoc XYZ", "symptoms": {"den do nhap nay": ["Kiem tra nguon dien", "Thay loi loc", "Lien he ky thuat"]}},
    "dong_ho": {"product": "Dong Ho Nam", "symptoms": {"khong len nguon": ["Sac pin", "Kiem tra nut nguon", "Reset"]}},
}