"""Mock Data - Cửa hàng thời trang & gia dụng StyleHub"""

# ─── KHÁCH HÀNG ────────────────────────────────────────────────────────────────

MOCK_CUSTOMERS = {
    "cust_001": {
        "customer_id": "cust_001", "name": "Nguyễn Văn An",
        "email": "nguyenvana@email.com", "phone": "0901234567",
        "address": {"street": "45 Nguyễn Trãi", "district": "Quận 1", "city": "TP.HCM"},
        "loyalty_tier": "gold", "total_spent": 5800000, "created_at": "2024-01-15T00:00:00Z",
    },
    "cust_002": {
        "customer_id": "cust_002", "name": "Trần Thị Bình",
        "email": "tranthib@email.com", "phone": "0912345678",
        "address": {"street": "12 Hoàng Diệu", "district": "Ba Đình", "city": "Hà Nội"},
        "loyalty_tier": "silver", "total_spent": 2100000, "created_at": "2024-02-20T00:00:00Z",
    },
    "cust_003": {
        "customer_id": "cust_003", "name": "Lê Minh Cảnh",
        "email": "leminhcanh@email.com", "phone": "0923456789",
        "address": {"street": "78 Trần Phú", "district": "Hải Châu", "city": "Đà Nẵng"},
        "loyalty_tier": "platinum", "total_spent": 15200000, "created_at": "2023-11-10T00:00:00Z",
    },
    "cust_004": {
        "customer_id": "cust_004", "name": "Phạm Thu Dung",
        "email": "phamthud@email.com", "phone": "0934567890",
        "address": {"street": "23 Lê Lợi", "district": "Ngô Quyền", "city": "Hải Phòng"},
        "loyalty_tier": "bronze", "total_spent": 750000, "created_at": "2024-06-01T00:00:00Z",
    },
    "cust_005": {
        "customer_id": "cust_005", "name": "Hoàng Đức Em",
        "email": "hoangduce@email.com", "phone": "0945678901",
        "address": {"street": "56 3 Tháng 2", "district": "Ninh Kiều", "city": "Cần Thơ"},
        "loyalty_tier": "gold", "total_spent": 4200000, "created_at": "2024-03-15T00:00:00Z",
    },
    "cust_006": {
        "customer_id": "cust_006", "name": "Vũ Thị Phương",
        "email": "vuthiphuong@email.com", "phone": "0956789012",
        "address": {"street": "88 Điện Biên Phủ", "district": "Bình Thạnh", "city": "TP.HCM"},
        "loyalty_tier": "silver", "total_spent": 1850000, "created_at": "2024-04-10T00:00:00Z",
    },
    "cust_007": {
        "customer_id": "cust_007", "name": "Đỗ Quốc Hùng",
        "email": "doquochung@email.com", "phone": "0967890123",
        "address": {"street": "34 Cầu Giấy", "district": "Cầu Giấy", "city": "Hà Nội"},
        "loyalty_tier": "platinum", "total_spent": 22500000, "created_at": "2023-08-20T00:00:00Z",
    },
    "cust_008": {
        "customer_id": "cust_008", "name": "Ngô Thị Lan",
        "email": "ngothilan@email.com", "phone": "0978901234",
        "address": {"street": "15 Nguyễn Hữu Thọ", "district": "Nhà Bè", "city": "TP.HCM"},
        "loyalty_tier": "bronze", "total_spent": 420000, "created_at": "2024-07-05T00:00:00Z",
    },
}

# ─── SẢN PHẨM ──────────────────────────────────────────────────────────────────
# tags: từ khóa không dấu để hỗ trợ tìm kiếm

MOCK_PRODUCTS = [
    # ── Thời trang Nam ──────────────────────────────────────────────────────────
    {
        "product_id": "prod_001", "name": "Áo Jacket Nam Oversize",
        "price": 590000, "original_price": 790000,
        "category": "nam", "rating": 4.6, "review_count": 128,
        "description": "Jacket dáng rộng streetwear, cotton pha polyester co giãn nhẹ, túi hộp phía trước",
        "colors": ["Navy", "Đen", "Xám"], "sizes": ["S", "M", "L", "XL"],
        "tags": ["ao jacket", "jacket", "ao khoac nam", "oversize", "jacket nam"],
    },
    {
        "product_id": "prod_002", "name": "Quần Jean Nam Slim Fit",
        "price": 350000, "original_price": None,
        "category": "nam", "rating": 4.4, "review_count": 203,
        "description": "Jean co giãn 4 chiều, form slim ôm vừa, wash nhạt thời trang Hàn Quốc",
        "colors": ["Xanh Nhạt", "Xanh Đậm", "Đen"], "sizes": ["28", "29", "30", "31", "32", "33", "34"],
        "tags": ["quan jean", "jean nam", "slim fit", "quan bo", "denim"],
    },
    {
        "product_id": "prod_003", "name": "Áo Polo Nam Cotton Pique",
        "price": 280000, "original_price": None,
        "category": "nam", "rating": 4.5, "review_count": 95,
        "description": "Polo cổ bẻ chất cotton pique thoáng mát, phù hợp đi làm và dạo phố",
        "colors": ["Trắng", "Navy", "Đỏ Bordeaux", "Xanh Lá"], "sizes": ["S", "M", "L", "XL", "XXL"],
        "tags": ["ao polo", "polo nam", "ao co be", "cotton", "ao nam"],
    },
    {
        "product_id": "prod_004", "name": "Áo Hoodie Unisex Basic",
        "price": 420000, "original_price": 520000,
        "category": "nam", "rating": 4.7, "review_count": 312,
        "description": "Hoodie nỉ bông dày, form rộng unisex, túi kangaroo, dây rút điều chỉnh",
        "colors": ["Đen", "Trắng", "Xám Đậm", "Be", "Xanh Pastel"], "sizes": ["S", "M", "L", "XL"],
        "tags": ["ao hoodie", "hoodie", "ao nui", "unisex", "ao thu dong"],
    },
    {
        "product_id": "prod_005", "name": "Quần Kaki Nam Công Sở",
        "price": 320000, "original_price": None,
        "category": "nam", "rating": 4.3, "review_count": 67,
        "description": "Kaki dáng straight, cotton pha co giãn, thích hợp mặc công sở lẫn đi chơi",
        "colors": ["Be", "Xám", "Nâu Đất", "Xanh Lính"], "sizes": ["28", "29", "30", "31", "32", "33"],
        "tags": ["quan kaki", "kaki nam", "quan cong so", "quan tay"],
    },
    # ── Thời trang Nữ ───────────────────────────────────────────────────────────
    {
        "product_id": "prod_006", "name": "Áo Sơ Mi Nữ Cổ Trụ Tay Dài",
        "price": 280000, "original_price": None,
        "category": "nu", "rating": 4.5, "review_count": 156,
        "description": "Sơ mi lụa mềm mại cổ trụ tay dài, phù hợp đi làm hoặc đi ăn tối",
        "colors": ["Trắng", "Đen", "Xanh Nhạt", "Hồng Pastel"], "sizes": ["XS", "S", "M", "L"],
        "tags": ["ao so mi", "so mi nu", "ao cong so nu", "ao tay dai"],
    },
    {
        "product_id": "prod_007", "name": "Váy Midi Hoa Nhí Dáng Xòe",
        "price": 450000, "original_price": 580000,
        "category": "nu", "rating": 4.6, "review_count": 89,
        "description": "Midi voan in hoa nhí dáng xòe nhẹ, nhẹ bay bổng, phong cách ngọt ngào",
        "colors": ["Xanh Hoa Trắng", "Hồng Hoa Vàng", "Tím Hoa Trắng"], "sizes": ["XS", "S", "M", "L"],
        "tags": ["vay midi", "vay hoa", "chan vay", "vay xoe", "dam xoe"],
    },
    {
        "product_id": "prod_008", "name": "Áo Khoác Nữ Tweed Houndstooth",
        "price": 890000, "original_price": 1200000,
        "category": "nu", "rating": 4.8, "review_count": 44,
        "description": "Blazer tweed họa tiết houndstooth sang trọng, dựng vai chuẩn, nút cúc đồng",
        "colors": ["Đen Trắng", "Nâu Kem"], "sizes": ["XS", "S", "M", "L"],
        "tags": ["ao khoac nu", "tweed", "blazer nu", "ao khoac thu dong"],
    },
    {
        "product_id": "prod_009", "name": "Đầm Dự Tiệc Satin Hai Dây",
        "price": 1200000, "original_price": None,
        "category": "nu", "rating": 4.7, "review_count": 62,
        "description": "Đầm satin bóng mượt, hai dây tinh tế, cut-out eo sau, dài chấm gối",
        "colors": ["Đỏ Rượu", "Đen", "Xanh Ngọc"], "sizes": ["XS", "S", "M", "L"],
        "tags": ["dam du tiec", "dam satin", "dam hai day", "du tiec", "vay dam"],
    },
    {
        "product_id": "prod_010", "name": "Áo Blouse Nữ Thắt Nơ Cổ",
        "price": 320000, "original_price": None,
        "category": "nu", "rating": 4.4, "review_count": 113,
        "description": "Blouse lụa nhân tạo mềm mịn, thắt nơ cổ thanh lịch, form suông nhẹ",
        "colors": ["Trắng", "Kem", "Xanh Baby", "Hồng Phấn"], "sizes": ["XS", "S", "M", "L", "XL"],
        "tags": ["ao blouse", "blouse nu", "ao that no", "ao cong so nu"],
    },
    # ── Giày Dép ────────────────────────────────────────────────────────────────
    {
        "product_id": "prod_011", "name": "Giày Sneaker Nam Cổ Cao",
        "price": 890000, "original_price": None,
        "category": "giay", "rating": 4.5, "review_count": 201,
        "description": "Sneaker cổ cao phong cách vintage, đế cao su chống trơn, đệm lót êm ái",
        "colors": ["Trắng/Đen", "All Black", "Trắng/Đỏ"], "sizes": ["38", "39", "40", "41", "42", "43", "44"],
        "tags": ["giay sneaker", "sneaker nam", "giay the thao", "giay co cao"],
    },
    {
        "product_id": "prod_012", "name": "Giày Cao Gót Nữ Block Heel 7cm",
        "price": 650000, "original_price": 850000,
        "category": "giay", "rating": 4.3, "review_count": 78,
        "description": "Cao gót gót vuông 7cm ổn định, da PU mềm, dây quai mắt cá điều chỉnh",
        "colors": ["Đen", "Nude", "Trắng", "Đỏ"], "sizes": ["35", "36", "37", "38", "39"],
        "tags": ["giay cao got", "cao got nu", "giot vuong", "block heel", "giay nu"],
    },
    {
        "product_id": "prod_013", "name": "Dép Sandal Nữ Đế Phẳng",
        "price": 280000, "original_price": None,
        "category": "giay", "rating": 4.4, "review_count": 134,
        "description": "Sandal dây quai chéo mảnh, đế phẳng nhẹ, phù hợp đi biển và dạo phố",
        "colors": ["Be", "Đen", "Trắng", "Vàng Ánh Kim"], "sizes": ["35", "36", "37", "38", "39", "40"],
        "tags": ["dep sandal", "sandal nu", "dep de phang", "dep mua he"],
    },
    {
        "product_id": "prod_014", "name": "Giày Thể Thao Running Unisex",
        "price": 750000, "original_price": 950000,
        "category": "giay", "rating": 4.6, "review_count": 267,
        "description": "Running shoes đế cushion chống sốc, lưới thoáng khí, phù hợp chạy bộ và gym",
        "colors": ["Trắng/Xanh", "Đen/Đỏ", "Xám/Cam"], "sizes": ["36", "37", "38", "39", "40", "41", "42", "43", "44"],
        "tags": ["giay the thao", "running shoes", "giay chay bo", "giay gym", "unisex"],
    },
    # ── Phụ Kiện ────────────────────────────────────────────────────────────────
    {
        "product_id": "prod_015", "name": "Túi Xách Nữ Da PU Cỡ Lớn",
        "price": 1800000, "original_price": None,
        "category": "phu kien", "rating": 4.5, "review_count": 88,
        "description": "Túi tote da PU cao cấp cỡ lớn, ngăn kéo khóa, có thể đeo vai hoặc cầm tay",
        "colors": ["Đen", "Nâu Caramel", "Kem", "Đỏ Đô"], "sizes": ["One Size"],
        "tags": ["tui xach nu", "tui tote", "tui da pu", "tui hang ngay"],
    },
    {
        "product_id": "prod_016", "name": "Đồng Hồ Nam Thể Thao Chronograph",
        "price": 1500000, "original_price": 2000000,
        "category": "phu kien", "rating": 4.6, "review_count": 143,
        "description": "Đồng hồ chronograph mặt tròn, dây cao su bền, chống nước 5ATM, pin 2 năm",
        "colors": ["Đen/Đen", "Bạc/Xanh Navy"], "sizes": ["One Size"],
        "tags": ["dong ho nam", "dong ho the thao", "chronograph", "chong nuoc", "dong ho"],
    },
    {
        "product_id": "prod_017", "name": "Ví Da Nam Gập Đôi",
        "price": 450000, "original_price": None,
        "category": "phu kien", "rating": 4.4, "review_count": 56,
        "description": "Ví da bò thật gập đôi, 8 ngăn thẻ, ngăn tiền mặt rộng, chống RFID",
        "colors": ["Đen", "Nâu Da Bò"], "sizes": ["One Size"],
        "tags": ["vi da nam", "vi nam", "vi gap doi", "phu kien nam"],
    },
    {
        "product_id": "prod_018", "name": "Kính Râm Gọng Tròn UV400",
        "price": 380000, "original_price": 480000,
        "category": "phu kien", "rating": 4.3, "review_count": 197,
        "description": "Kính mát gọng tròn vintage, tròng UV400 chống 100% tia UVA/UVB, khung nhẹ",
        "colors": ["Đen/Vàng", "Nâu/Vàng", "Bạc/Xám"], "sizes": ["One Size"],
        "tags": ["kinh mat", "kinh ram", "sunglasses", "uv400", "kinh gong tron"],
    },
    # ── Gia Dụng ────────────────────────────────────────────────────────────────
    {
        "product_id": "prod_019", "name": "Máy Lọc Nước RO 9 Cấp",
        "price": 2500000, "original_price": 3200000,
        "category": "gia dung", "rating": 4.7, "review_count": 312,
        "description": "Máy lọc RO 9 lõi lọc, loại 99.9% vi khuẩn và tạp chất, lưu lượng 10L/h, van tự ngắt",
        "colors": ["Trắng"], "sizes": ["One Size"],
        "tags": ["may loc nuoc", "loc nuoc ro", "nuoc sach", "gia dung bep", "ro"],
    },
    {
        "product_id": "prod_020", "name": "Bình Giữ Nhiệt Inox 500ml",
        "price": 250000, "original_price": None,
        "category": "gia dung", "rating": 4.8, "review_count": 445,
        "description": "Bình inox 316 cao cấp, giữ nóng 12h/lạnh 24h, nắp xoay kín, dung tích 500ml",
        "colors": ["Trắng Sứ", "Bạc", "Đen Nhám", "Hồng Đào"], "sizes": ["500ml"],
        "tags": ["binh giu nhiet", "binh nuoc", "thermal bottle", "inox", "binh nuoc giu nhiet"],
    },
]

MOCK_PRODUCTS_BY_ID = {p["product_id"]: p for p in MOCK_PRODUCTS}

# ─── TỒN KHO ────────────────────────────────────────────────────────────────────

MOCK_STOCK = {
    "prod_001": {"product_id": "prod_001", "in_stock": True, "variants": [
        {"color": "Navy", "size": "S", "qty": 15, "available": True},
        {"color": "Navy", "size": "M", "qty": 8, "available": True},
        {"color": "Navy", "size": "L", "qty": 12, "available": True},
        {"color": "Navy", "size": "XL", "qty": 0, "available": False},
        {"color": "Đen", "size": "M", "qty": 20, "available": True},
        {"color": "Xám", "size": "L", "qty": 10, "available": True},
    ]},
    "prod_009": {"product_id": "prod_009", "in_stock": True, "variants": [
        {"color": "Đỏ Rượu", "size": "XS", "qty": 3, "available": True},
        {"color": "Đỏ Rượu", "size": "S", "qty": 7, "available": True},
        {"color": "Đỏ Rượu", "size": "M", "qty": 0, "available": False},
        {"color": "Đen", "size": "S", "qty": 5, "available": True},
        {"color": "Xanh Ngọc", "size": "S", "qty": 2, "available": True},
    ]},
    "prod_019": {"product_id": "prod_019", "in_stock": True, "variants": [
        {"color": "Trắng", "size": "One Size", "qty": 30, "available": True},
    ]},
    "prod_020": {"product_id": "prod_020", "in_stock": True, "variants": [
        {"color": "Trắng Sứ", "size": "500ml", "qty": 50, "available": True},
        {"color": "Đen Nhám", "size": "500ml", "qty": 35, "available": True},
        {"color": "Hồng Đào", "size": "500ml", "qty": 0, "available": False},
    ]},
}

# ─── ĐƠN HÀNG ───────────────────────────────────────────────────────────────────

MOCK_ORDERS = {
    # ── cust_001: Nguyễn Văn An (Gold) ──────────────────────────────────────────
    "ORD-12345": {
        "order_id": "ORD-12345", "customer_id": "cust_001", "status": "shipped",
        "items": [
            {"product_id": "prod_001", "name": "Áo Jacket Nam Oversize", "color": "Navy", "size": "L", "qty": 1, "price": 590000},
        ],
        "total": 590000, "shipping_fee": 0,
        "payment_method": "Thẻ Visa ****4242",
        "shipping_address": {"street": "45 Nguyễn Trãi", "district": "Quận 1", "city": "TP.HCM"},
        "created_at": "2026-09-10T10:00:00Z", "tracking_number": "TRK-789", "carrier": "GHN",
    },
    "ORD-12346": {
        "order_id": "ORD-12346", "customer_id": "cust_001", "status": "delivered",
        "items": [
            {"product_id": "prod_001", "name": "Áo Jacket Nam Oversize", "color": "Navy", "size": "L", "qty": 1, "price": 590000},
        ],
        "total": 590000, "shipping_fee": 0,
        "payment_method": "MoMo",
        "shipping_address": {"street": "45 Nguyễn Trãi", "district": "Quận 1", "city": "TP.HCM"},
        "created_at": "2026-08-20T14:30:00Z", "tracking_number": "TRK-A002", "carrier": "Viettel Post",
        "delivered_at": "2026-08-24T09:00:00Z",
    },
    "ORD-10001": {
        "order_id": "ORD-10001", "customer_id": "cust_001", "status": "shipped",
        "items": [
            {"product_id": "prod_001", "name": "Áo Jacket Nam Oversize", "color": "Navy", "size": "L", "qty": 1, "price": 590000},
            {"product_id": "prod_011", "name": "Giày Sneaker Nam Cổ Cao", "color": "Trắng/Đen", "size": "42", "qty": 1, "price": 890000},
        ],
        "total": 1480000, "shipping_fee": 0,
        "payment_method": "Thẻ Visa ****4242",
        "shipping_address": {"street": "45 Nguyễn Trãi", "district": "Quận 1", "city": "TP.HCM"},
        "created_at": "2026-09-10T10:00:00Z", "tracking_number": "TRK-A001", "carrier": "GHN",
    },
    "ORD-10002": {
        "order_id": "ORD-10002", "customer_id": "cust_001", "status": "delivered",
        "items": [
            {"product_id": "prod_002", "name": "Quần Jean Nam Slim Fit", "color": "Xanh Nhạt", "size": "30", "qty": 1, "price": 350000},
            {"product_id": "prod_003", "name": "Áo Polo Nam Cotton Pique", "color": "Navy", "size": "L", "qty": 2, "price": 560000},
        ],
        "total": 910000, "shipping_fee": 0,
        "payment_method": "MoMo",
        "shipping_address": {"street": "45 Nguyễn Trãi", "district": "Quận 1", "city": "TP.HCM"},
        "created_at": "2026-08-20T14:30:00Z", "tracking_number": "TRK-A002", "carrier": "Viettel Post",
        "delivered_at": "2026-08-24T09:00:00Z",
    },
    "ORD-10003": {
        "order_id": "ORD-10003", "customer_id": "cust_001", "status": "processing",
        "items": [
            {"product_id": "prod_019", "name": "Máy Lọc Nước RO 9 Cấp", "color": "Trắng", "size": "One Size", "qty": 1, "price": 2500000},
        ],
        "total": 2500000, "shipping_fee": 30000,
        "payment_method": "VNPay",
        "shipping_address": {"street": "45 Nguyễn Trãi", "district": "Quận 1", "city": "TP.HCM"},
        "created_at": "2026-09-18T08:00:00Z",
    },
    # ── cust_002: Trần Thị Bình (Silver) ────────────────────────────────────────
    "ORD-20001": {
        "order_id": "ORD-20001", "customer_id": "cust_002", "status": "processing",
        "items": [
            {"product_id": "prod_006", "name": "Áo Sơ Mi Nữ Cổ Trụ Tay Dài", "color": "Trắng", "size": "M", "qty": 1, "price": 280000},
            {"product_id": "prod_010", "name": "Áo Blouse Nữ Thắt Nơ Cổ", "color": "Kem", "size": "S", "qty": 1, "price": 320000},
        ],
        "total": 600000, "shipping_fee": 30000,
        "payment_method": "ZaloPay",
        "shipping_address": {"street": "12 Hoàng Diệu", "district": "Ba Đình", "city": "Hà Nội"},
        "created_at": "2026-09-17T11:00:00Z",
    },
    "ORD-20002": {
        "order_id": "ORD-20002", "customer_id": "cust_002", "status": "pending",
        "items": [
            {"product_id": "prod_009", "name": "Đầm Dự Tiệc Satin Hai Dây", "color": "Đỏ Rượu", "size": "S", "qty": 1, "price": 1200000},
        ],
        "total": 1200000, "shipping_fee": 0,
        "payment_method": "COD",
        "shipping_address": {"street": "12 Hoàng Diệu", "district": "Ba Đình", "city": "Hà Nội"},
        "created_at": "2026-09-19T09:30:00Z",
    },
    # ── cust_003: Lê Minh Cảnh (Platinum) ───────────────────────────────────────
    "ORD-30001": {
        "order_id": "ORD-30001", "customer_id": "cust_003", "status": "delivered",
        "items": [
            {"product_id": "prod_015", "name": "Túi Xách Nữ Da PU Cỡ Lớn", "color": "Đen", "size": "One Size", "qty": 1, "price": 1800000},
            {"product_id": "prod_018", "name": "Kính Râm Gọng Tròn UV400", "color": "Đen/Vàng", "size": "One Size", "qty": 1, "price": 380000},
        ],
        "total": 2180000, "shipping_fee": 0,
        "payment_method": "Thẻ Visa ****1234",
        "shipping_address": {"street": "78 Trần Phú", "district": "Hải Châu", "city": "Đà Nẵng"},
        "created_at": "2026-08-15T16:00:00Z", "tracking_number": "TRK-C001", "carrier": "GHN",
        "delivered_at": "2026-08-19T14:00:00Z",
    },
    "ORD-30002": {
        "order_id": "ORD-30002", "customer_id": "cust_003", "status": "cancelled",
        "items": [
            {"product_id": "prod_014", "name": "Giày Thể Thao Running Unisex", "color": "Trắng/Xanh", "size": "42", "qty": 1, "price": 750000},
        ],
        "total": 750000, "shipping_fee": 0,
        "payment_method": "MoMo",
        "shipping_address": {"street": "78 Trần Phú", "district": "Hải Châu", "city": "Đà Nẵng"},
        "created_at": "2026-09-01T10:00:00Z",
        "cancelled_at": "2026-09-01T15:00:00Z", "cancel_reason": "Khách đổi ý",
    },
    "ORD-30003": {
        "order_id": "ORD-30003", "customer_id": "cust_003", "status": "shipped",
        "items": [
            {"product_id": "prod_016", "name": "Đồng Hồ Nam Thể Thao Chronograph", "color": "Đen/Đen", "size": "One Size", "qty": 1, "price": 1500000},
            {"product_id": "prod_017", "name": "Ví Da Nam Gập Đôi", "color": "Đen", "size": "One Size", "qty": 1, "price": 450000},
        ],
        "total": 1950000, "shipping_fee": 0,
        "payment_method": "Thẻ Visa ****1234",
        "shipping_address": {"street": "78 Trần Phú", "district": "Hải Châu", "city": "Đà Nẵng"},
        "created_at": "2026-09-15T09:00:00Z", "tracking_number": "TRK-C002", "carrier": "J&T Express",
    },
    # ── cust_004: Phạm Thu Dung (Bronze) ────────────────────────────────────────
    "ORD-40001": {
        "order_id": "ORD-40001", "customer_id": "cust_004", "status": "delivered",
        "items": [
            {"product_id": "prod_013", "name": "Dép Sandal Nữ Đế Phẳng", "color": "Be", "size": "37", "qty": 1, "price": 280000},
            {"product_id": "prod_020", "name": "Bình Giữ Nhiệt Inox 500ml", "color": "Hồng Đào", "size": "500ml", "qty": 1, "price": 250000},
        ],
        "total": 530000, "shipping_fee": 30000,
        "payment_method": "COD",
        "shipping_address": {"street": "23 Lê Lợi", "district": "Ngô Quyền", "city": "Hải Phòng"},
        "created_at": "2026-09-05T13:00:00Z", "tracking_number": "TRK-D001", "carrier": "GHTK",
        "delivered_at": "2026-09-08T10:00:00Z",
    },
    # ── cust_005: Hoàng Đức Em (Gold) ───────────────────────────────────────────
    "ORD-50001": {
        "order_id": "ORD-50001", "customer_id": "cust_005", "status": "delivered",
        "items": [
            {"product_id": "prod_004", "name": "Áo Hoodie Unisex Basic", "color": "Đen", "size": "L", "qty": 1, "price": 420000},
            {"product_id": "prod_005", "name": "Quần Kaki Nam Công Sở", "color": "Xám", "size": "31", "qty": 1, "price": 320000},
        ],
        "total": 740000, "shipping_fee": 0,
        "payment_method": "VNPay",
        "shipping_address": {"street": "56 3 Tháng 2", "district": "Ninh Kiều", "city": "Cần Thơ"},
        "created_at": "2026-09-01T08:00:00Z", "tracking_number": "TRK-E001", "carrier": "GHN",
        "delivered_at": "2026-09-04T11:00:00Z",
    },
    "ORD-50002": {
        "order_id": "ORD-50002", "customer_id": "cust_005", "status": "processing",
        "items": [
            {"product_id": "prod_008", "name": "Áo Khoác Nữ Tweed Houndstooth", "color": "Đen Trắng", "size": "M", "qty": 1, "price": 890000},
        ],
        "total": 890000, "shipping_fee": 0,
        "payment_method": "MoMo",
        "shipping_address": {"street": "56 3 Tháng 2", "district": "Ninh Kiều", "city": "Cần Thơ"},
        "created_at": "2026-09-18T15:30:00Z",
    },
    # ── cust_006: Vũ Thị Phương (Silver) ────────────────────────────────────────
    "ORD-60001": {
        "order_id": "ORD-60001", "customer_id": "cust_006", "status": "shipped",
        "items": [
            {"product_id": "prod_007", "name": "Váy Midi Hoa Nhí Dáng Xòe", "color": "Xanh Hoa Trắng", "size": "S", "qty": 1, "price": 450000},
            {"product_id": "prod_012", "name": "Giày Cao Gót Nữ Block Heel 7cm", "color": "Nude", "size": "37", "qty": 1, "price": 650000},
        ],
        "total": 1100000, "shipping_fee": 0,
        "payment_method": "Thẻ Mastercard ****5678",
        "shipping_address": {"street": "88 Điện Biên Phủ", "district": "Bình Thạnh", "city": "TP.HCM"},
        "created_at": "2026-09-16T10:00:00Z", "tracking_number": "TRK-F001", "carrier": "GHN",
    },
    "ORD-60002": {
        "order_id": "ORD-60002", "customer_id": "cust_006", "status": "pending",
        "items": [
            {"product_id": "prod_015", "name": "Túi Xách Nữ Da PU Cỡ Lớn", "color": "Nâu Caramel", "size": "One Size", "qty": 1, "price": 1800000},
        ],
        "total": 1800000, "shipping_fee": 0,
        "payment_method": "ZaloPay",
        "shipping_address": {"street": "88 Điện Biên Phủ", "district": "Bình Thạnh", "city": "TP.HCM"},
        "created_at": "2026-09-19T20:00:00Z",
    },
    # ── cust_007: Đỗ Quốc Hùng (Platinum) ──────────────────────────────────────
    "ORD-70001": {
        "order_id": "ORD-70001", "customer_id": "cust_007", "status": "delivered",
        "items": [
            {"product_id": "prod_019", "name": "Máy Lọc Nước RO 9 Cấp", "color": "Trắng", "size": "One Size", "qty": 1, "price": 2500000},
            {"product_id": "prod_020", "name": "Bình Giữ Nhiệt Inox 500ml", "color": "Đen Nhám", "size": "500ml", "qty": 2, "price": 500000},
        ],
        "total": 3000000, "shipping_fee": 0,
        "payment_method": "Thẻ Visa ****9999",
        "shipping_address": {"street": "34 Cầu Giấy", "district": "Cầu Giấy", "city": "Hà Nội"},
        "created_at": "2026-08-01T09:00:00Z", "tracking_number": "TRK-G001", "carrier": "Viettel Post",
        "delivered_at": "2026-08-05T14:00:00Z",
    },
    "ORD-70002": {
        "order_id": "ORD-70002", "customer_id": "cust_007", "status": "shipped",
        "items": [
            {"product_id": "prod_001", "name": "Áo Jacket Nam Oversize", "color": "Đen", "size": "XL", "qty": 1, "price": 590000},
            {"product_id": "prod_002", "name": "Quần Jean Nam Slim Fit", "color": "Đen", "size": "32", "qty": 1, "price": 350000},
            {"product_id": "prod_004", "name": "Áo Hoodie Unisex Basic", "color": "Xám Đậm", "size": "XL", "qty": 1, "price": 420000},
        ],
        "total": 1360000, "shipping_fee": 0,
        "payment_method": "Thẻ Visa ****9999",
        "shipping_address": {"street": "34 Cầu Giấy", "district": "Cầu Giấy", "city": "Hà Nội"},
        "created_at": "2026-09-12T14:00:00Z", "tracking_number": "TRK-G002", "carrier": "GHN",
    },
    "ORD-70003": {
        "order_id": "ORD-70003", "customer_id": "cust_007", "status": "processing",
        "items": [
            {"product_id": "prod_016", "name": "Đồng Hồ Nam Thể Thao Chronograph", "color": "Bạc/Xanh Navy", "size": "One Size", "qty": 1, "price": 1500000},
        ],
        "total": 1500000, "shipping_fee": 0,
        "payment_method": "ZaloPay",
        "shipping_address": {"street": "34 Cầu Giấy", "district": "Cầu Giấy", "city": "Hà Nội"},
        "created_at": "2026-09-19T16:00:00Z",
    },
    # ── cust_008: Ngô Thị Lan (Bronze) ──────────────────────────────────────────
    "ORD-80001": {
        "order_id": "ORD-80001", "customer_id": "cust_008", "status": "pending",
        "items": [
            {"product_id": "prod_006", "name": "Áo Sơ Mi Nữ Cổ Trụ Tay Dài", "color": "Hồng Pastel", "size": "XS", "qty": 1, "price": 280000},
        ],
        "total": 280000, "shipping_fee": 30000,
        "payment_method": "COD",
        "shipping_address": {"street": "15 Nguyễn Hữu Thọ", "district": "Nhà Bè", "city": "TP.HCM"},
        "created_at": "2026-09-19T22:00:00Z",
    },
}

# ─── VẬN CHUYỂN ─────────────────────────────────────────────────────────────────

MOCK_SHIPPING = {
    "TRK-789": {
        "tracking_number": "TRK-789", "carrier": "GHN",
        "current_status": "in_transit", "estimated_delivery": "2026-09-21", "is_delayed": False,
        "checkpoints": [
            {"time": "2026-09-10T12:00:00Z", "location": "HCM - Kho gửi hàng", "note": "Đã lấy hàng"},
            {"time": "2026-09-11T08:00:00Z", "location": "HCM - Trung tâm phân loại", "note": "Đang vận chuyển"},
        ],
    },
    "TRK-A001": {
        "tracking_number": "TRK-A001", "carrier": "GHN",
        "current_status": "in_transit", "estimated_delivery": "2026-09-21", "is_delayed": False,
        "checkpoints": [
            {"time": "2026-09-10T12:00:00Z", "location": "HCM - Kho gửi hàng", "note": "Đã lấy hàng"},
            {"time": "2026-09-11T08:00:00Z", "location": "HCM - Trung tâm phân loại", "note": "Đang vận chuyển"},
        ],
    },
    "TRK-A002": {
        "tracking_number": "TRK-A002", "carrier": "Viettel Post",
        "current_status": "delivered", "estimated_delivery": "2026-08-24", "is_delayed": False,
        "delivered_at": "2026-08-24T09:00:00Z",
    },
    "TRK-C001": {
        "tracking_number": "TRK-C001", "carrier": "GHN",
        "current_status": "delivered", "estimated_delivery": "2026-08-19", "is_delayed": False,
        "delivered_at": "2026-08-19T14:00:00Z",
    },
    "TRK-C002": {
        "tracking_number": "TRK-C002", "carrier": "J&T Express",
        "current_status": "in_transit", "estimated_delivery": "2026-09-17", "is_delayed": True,
        "delay_reason": "Bão số 3 làm chậm vận chuyển khu vực miền Trung",
    },
    "TRK-D001": {
        "tracking_number": "TRK-D001", "carrier": "GHTK",
        "current_status": "delivered", "estimated_delivery": "2026-09-08", "is_delayed": False,
        "delivered_at": "2026-09-08T10:00:00Z",
    },
    "TRK-E001": {
        "tracking_number": "TRK-E001", "carrier": "GHN",
        "current_status": "delivered", "estimated_delivery": "2026-09-04", "is_delayed": False,
        "delivered_at": "2026-09-04T11:00:00Z",
    },
    "TRK-F001": {
        "tracking_number": "TRK-F001", "carrier": "GHN",
        "current_status": "in_transit", "estimated_delivery": "2026-09-18", "is_delayed": True,
        "delay_reason": "Địa chỉ khó tìm, shipper sẽ gọi điện trước khi giao",
    },
    "TRK-G001": {
        "tracking_number": "TRK-G001", "carrier": "Viettel Post",
        "current_status": "delivered", "estimated_delivery": "2026-08-05", "is_delayed": False,
        "delivered_at": "2026-08-05T14:00:00Z",
    },
    "TRK-G002": {
        "tracking_number": "TRK-G002", "carrier": "GHN",
        "current_status": "in_transit", "estimated_delivery": "2026-09-14", "is_delayed": True,
        "delay_reason": "Hàng đang chờ tại kho trung chuyển Hà Nội do tắc đường",
    },
}

# ─── THANH TOÁN ─────────────────────────────────────────────────────────────────

MOCK_PAYMENTS = {
    "ORD-12345": {"payment_id": "PAY-12345", "order_id": "ORD-12345", "customer_id": "cust_001", "status": "paid", "amount": 590000, "method": "Thẻ Visa ****4242", "paid_at": "2026-09-10T10:05:00Z"},
    "ORD-10001": {"payment_id": "PAY-A001", "order_id": "ORD-10001", "customer_id": "cust_001", "status": "paid", "amount": 1480000, "method": "Thẻ Visa ****4242", "paid_at": "2026-09-10T10:05:00Z"},
    "ORD-10002": {"payment_id": "PAY-A002", "order_id": "ORD-10002", "customer_id": "cust_001", "status": "paid", "amount": 910000, "method": "MoMo", "paid_at": "2026-08-20T14:32:00Z"},
    "ORD-10003": {"payment_id": "PAY-A003", "order_id": "ORD-10003", "customer_id": "cust_001", "status": "paid", "amount": 2530000, "method": "VNPay", "paid_at": "2026-09-18T08:02:00Z"},
    "ORD-20001": {"payment_id": "PAY-B001", "order_id": "ORD-20001", "customer_id": "cust_002", "status": "paid", "amount": 630000, "method": "ZaloPay", "paid_at": "2026-09-17T11:03:00Z"},
    "ORD-30001": {"payment_id": "PAY-C001", "order_id": "ORD-30001", "customer_id": "cust_003", "status": "paid", "amount": 2180000, "method": "Thẻ Visa ****1234", "paid_at": "2026-08-15T16:05:00Z"},
    "ORD-30003": {"payment_id": "PAY-C002", "order_id": "ORD-30003", "customer_id": "cust_003", "status": "paid", "amount": 1950000, "method": "Thẻ Visa ****1234", "paid_at": "2026-09-15T09:02:00Z"},
    "ORD-40001": {"payment_id": "PAY-D001", "order_id": "ORD-40001", "customer_id": "cust_004", "status": "paid", "amount": 560000, "method": "COD", "paid_at": "2026-09-08T10:00:00Z"},
    "ORD-50001": {"payment_id": "PAY-E001", "order_id": "ORD-50001", "customer_id": "cust_005", "status": "paid", "amount": 740000, "method": "VNPay", "paid_at": "2026-09-01T08:03:00Z"},
    "ORD-50002": {"payment_id": "PAY-E002", "order_id": "ORD-50002", "customer_id": "cust_005", "status": "paid", "amount": 890000, "method": "MoMo", "paid_at": "2026-09-18T15:32:00Z"},
    "ORD-60001": {"payment_id": "PAY-F001", "order_id": "ORD-60001", "customer_id": "cust_006", "status": "paid", "amount": 1100000, "method": "Thẻ Mastercard ****5678", "paid_at": "2026-09-16T10:03:00Z"},
    "ORD-70001": {"payment_id": "PAY-G001", "order_id": "ORD-70001", "customer_id": "cust_007", "status": "paid", "amount": 3000000, "method": "Thẻ Visa ****9999", "paid_at": "2026-08-01T09:05:00Z"},
    "ORD-70002": {"payment_id": "PAY-G002", "order_id": "ORD-70002", "customer_id": "cust_007", "status": "paid", "amount": 1360000, "method": "Thẻ Visa ****9999", "paid_at": "2026-09-12T14:02:00Z"},
    "ORD-70003": {"payment_id": "PAY-G003", "order_id": "ORD-70003", "customer_id": "cust_007", "status": "paid", "amount": 1500000, "method": "ZaloPay", "paid_at": "2026-09-19T16:01:00Z"},
}

# ─── HÓA ĐƠN ────────────────────────────────────────────────────────────────────

MOCK_INVOICES = {
    "ORD-10001": {"invoice_id": "INV-A001", "total": 1480000, "status": "paid"},
    "ORD-10002": {"invoice_id": "INV-A002", "total": 910000, "status": "paid"},
    "ORD-30001": {"invoice_id": "INV-C001", "total": 2180000, "status": "paid"},
    "ORD-70001": {"invoice_id": "INV-G001", "total": 3000000, "status": "paid"},
    "ORD-70002": {"invoice_id": "INV-G002", "total": 1360000, "status": "paid"},
}

# ─── BÀI VIẾT KIẾN THỨC ─────────────────────────────────────────────────────────

MOCK_KB_ARTICLES = [
    {
        "id": "KB-001", "title": "Chính sách đổi trả", "category": "policy",
        "content": "Đổi/trả trong 30 ngày từ ngày nhận hàng. Điều kiện: còn nguyên tem nhãn, chưa sử dụng, đủ phụ kiện và hóa đơn. Không áp dụng đồ lót, đồ bơi và hàng giảm >50%.",
        "tags": ["doi tra", "chinh sach", "30 ngay", "tra hang", "doi hang"],
        "relevance_score": 0.9,
    },
    {
        "id": "KB-002", "title": "Chính sách hoàn tiền", "category": "policy",
        "content": "Hoàn về phương thức gốc trong 5-7 ngày làm việc. Với COD hoàn qua chuyển khoản 7-10 ngày. Thẻ ngân hàng có thể mất thêm 1-3 ngày tùy ngân hàng.",
        "tags": ["hoan tien", "refund", "chinh sach", "tra tien"],
        "relevance_score": 0.9,
    },
    {
        "id": "KB-003", "title": "Theo dõi đơn hàng", "category": "guide",
        "content": "Cung cấp mã đơn hàng (ORD-XXXXX) hoặc mã vận đơn (TRK-XXXXX) để tra cứu. Nội thành 1-2 ngày. Tỉnh thành 2-5 ngày. Giao hỏa tốc trong 2-4h (phí thêm 50.000đ).",
        "tags": ["theo doi don hang", "van don", "giao hang", "tracking", "don hang"],
        "relevance_score": 0.85,
    },
    {
        "id": "KB-004", "title": "Máy lọc nước — Hướng dẫn & Xử lý sự cố", "category": "guide",
        "content": "Đèn đỏ nhấp nháy: kiểm tra nguồn điện và van xả. Không ra nước: mở van đầu vào, kiểm tra áp suất ≥2 bar. Nước có mùi lạ: thay lõi than hoạt tính. Liên hệ kỹ thuật nếu không tự xử lý được.",
        "tags": ["may loc nuoc", "den do", "khong ra nuoc", "bao tri", "sua chua", "ro"],
        "relevance_score": 0.9,
    },
    {
        "id": "KB-005", "title": "Phương thức thanh toán", "category": "faq",
        "content": "Chấp nhận: Visa/Mastercard, VNPay, MoMo, ZaloPay, COD. Đơn ≥1 triệu hỗ trợ trả góp 0% qua thẻ tín dụng 3-12 tháng (Sacombank, VPBank, Shinhan).",
        "tags": ["thanh toan", "visa", "momo", "vnpay", "zalopay", "cod", "tra gop"],
        "relevance_score": 0.85,
    },
    {
        "id": "KB-006", "title": "Chính sách vận chuyển & phí ship", "category": "policy",
        "content": "Miễn phí ship đơn từ 500.000đ. Phí tiêu chuẩn: nội thành 30.000đ, tỉnh 40.000đ. Đối tác: GHN, Viettel Post, J&T Express, GHTK. Thành viên Platinum miễn phí ship mọi đơn.",
        "tags": ["van chuyen", "phi ship", "mien phi ship", "giao hang", "shipping"],
        "relevance_score": 0.85,
    },
    {
        "id": "KB-007", "title": "Thanh toán bị trừ 2 lần", "category": "faq",
        "content": "Cung cấp: mã giao dịch, ảnh sao kê ngân hàng, mã đơn hàng. Kế toán xử lý trong 2-3 ngày làm việc. Hoàn tiền trong 3-5 ngày. Hotline: 1800-xxxx (miễn phí, 8h-22h).",
        "tags": ["tru 2 lan", "double charge", "loi thanh toan", "khieu nai", "sao ke"],
        "relevance_score": 0.9,
    },
    {
        "id": "KB-008", "title": "Chính sách bảo hành", "category": "policy",
        "content": "Gia dụng/điện tử: 12 tháng. Giày dép: 3 tháng (lỗi đế, đường may). Phụ kiện: 6 tháng. Thời trang: 30 ngày (lỗi vải, đường chỉ). Không bảo hành hư hỏng do sử dụng.",
        "tags": ["bao hanh", "warranty", "loi san xuat", "bao hanh san pham"],
        "relevance_score": 0.85,
    },
    {
        "id": "KB-009", "title": "Hủy đơn hàng", "category": "faq",
        "content": "Hủy trong 2 giờ sau đặt hoặc khi đơn ở trạng thái Pending/Đang xử lý. Đơn đã bàn giao vận chuyển không thể hủy — cần làm thủ tục hoàn hàng sau khi nhận.",
        "tags": ["huy don", "cancel order", "huy hang", "huy dat hang"],
        "relevance_score": 0.85,
    },
    {
        "id": "KB-010", "title": "Ưu đãi thành viên VIP", "category": "faq",
        "content": "Bronze: không giảm thêm. Silver: -3% mọi đơn. Gold: -5% + hỗ trợ ưu tiên. Platinum: -10% + miễn phí ship + quà sinh nhật + đường dây riêng. Hạng thăng sau 3 tháng tích lũy.",
        "tags": ["vip", "thanh vien", "uu dai", "giam gia", "loyalty", "hang thanh vien"],
        "relevance_score": 0.8,
    },
    {
        "id": "KB-011", "title": "Hướng dẫn chọn size giày", "category": "guide",
        "content": "Đo chiều dài bàn chân khi đứng (gót đến ngón dài nhất). Size VN: 36=23cm, 37=23.5cm, 38=24cm, 39=25cm, 40=26cm, 41=26.5cm, 42=27cm. Chân rộng chọn +0.5 size.",
        "tags": ["size giay", "huong dan", "chon size", "do size", "co giay"],
        "relevance_score": 0.85,
    },
    {
        "id": "KB-012", "title": "Chăm sóc & bảo quản sản phẩm", "category": "guide",
        "content": "Áo/Quần: giặt nhẹ 30°C, không tẩy, phơi tránh nắng trực tiếp. Giày da/PU: lau khô, tránh ẩm, bảo quản trong hộp. Túi xách: nhồi giấy báo giữ form, tránh treo lâu ngày.",
        "tags": ["cham soc", "giat", "bao quan", "thoi trang", "giay da"],
        "relevance_score": 0.8,
    },
    {
        "id": "KB-013", "title": "Flash Sale & Voucher giảm giá", "category": "faq",
        "content": "Flash Sale 12h và 20h mỗi ngày, giảm đến 70%. Nhập WELCOME10 giảm 10% đơn đầu. Voucher sinh nhật tặng riêng. Theo dõi Zalo OA và Facebook để nhận mã mới nhất.",
        "tags": ["giam gia", "khuyen mai", "voucher", "flash sale", "ma giam gia", "sale"],
        "relevance_score": 0.8,
    },
    {
        "id": "KB-014", "title": "Sản phẩm lỗi — Khiếu nại", "category": "policy",
        "content": "Chụp ảnh sản phẩm lỗi rõ ràng. Liên hệ trong 48h sau nhận hàng qua chat hoặc hotline. Gửi kèm mã đơn + ảnh lỗi. Xử lý đổi hàng hoặc hoàn tiền trong 1-3 ngày làm việc.",
        "tags": ["san pham loi", "khieu nai", "hang loi", "doi hang loi", "loi ky thuat"],
        "relevance_score": 0.85,
    },
    {
        "id": "KB-015", "title": "Giao hàng nhanh & hỏa tốc", "category": "guide",
        "content": "Hỏa tốc (2-4h): nội thành HCM và HN, phí 50.000đ, đặt trước 19h. Same-day: đặt trước 11h, giao trong ngày. Tỉnh thành 2-5 ngày tùy đơn vị vận chuyển.",
        "tags": ["giao hang nhanh", "hoa toc", "same day", "express delivery"],
        "relevance_score": 0.8,
    },
]

MOCK_KB_BY_ID = {a["id"]: a for a in MOCK_KB_ARTICLES}

# ─── CHÍNH SÁCH ĐỔI TRẢ ─────────────────────────────────────────────────────────

RETURN_POLICY = {
    "return_window_days": 30,
    "refund_timeline": "5-7 ngày làm việc",
    "cod_refund_timeline": "7-10 ngày",
    "high_value_threshold": 500000,
    "conditions": [
        "Còn nguyên tem, nhãn mác đầy đủ",
        "Chưa qua sử dụng",
        "Đầy đủ phụ kiện và hóa đơn mua hàng",
        "Không có dấu hiệu hư hỏng do người dùng",
    ],
    "non_returnable": ["Đồ lót", "Đồ bơi", "Sản phẩm đã giảm giá trên 50%"],
    "contact": "Chat trực tiếp hoặc Hotline 1800-xxxx (8h-22h, miễn phí)",
}

# ─── HƯỚNG DẪN XỬ LÝ SỰ CỐ ─────────────────────────────────────────────────────

TROUBLESHOOTING_GUIDES = {
    "may_loc_nuoc": {
        "product": "Máy Lọc Nước RO 9 Cấp",
        "symptoms": {
            "den do nhap nay": [
                "Kiểm tra nguồn điện 220V có ổn định không",
                "Kiểm tra van xả áp, xoay mở hoàn toàn",
                "Thay lõi lọc nếu đã dùng quá 6 tháng",
                "Liên hệ kỹ thuật viên nếu vẫn không khắc phục được",
            ],
            "khong ra nuoc": [
                "Mở hoàn toàn van đầu vào nước",
                "Kiểm tra áp suất nước đầu vào (≥2 bar)",
                "Kiểm tra bình áp có bị xẹp không",
                "Xả khí bình chứa: mở vòi và chờ 2-3 phút",
            ],
            "nuoc co mui la": [
                "Thay lõi lọc than hoạt tính (lõi số 3 và 5)",
                "Vệ sinh bình chứa bằng nước sôi",
                "Thay lõi RO nếu đã dùng quá 24 tháng",
            ],
        },
    },
    "binh_giu_nhiet": {
        "product": "Bình Giữ Nhiệt Inox 500ml",
        "symptoms": {
            "khong giu nhiet": [
                "Kiểm tra nắp đã vặn chặt hoàn toàn chưa",
                "Tránh để bình tiếp xúc với bề mặt kim loại lạnh/nóng",
                "Thay gioăng cao su nắp nếu bị mòn hoặc nứt",
            ],
            "kho mo nap": [
                "Đổ nước ấm (không nóng) lên bên ngoài nắp 30 giây",
                "Xoay ngược chiều kim đồng hồ với lực mạnh hơn",
                "Dùng khăn vải để tăng ma sát khi mở",
            ],
        },
    },
    "giay_the_thao": {
        "product": "Giày Thể Thao Running Unisex",
        "symptoms": {
            "de bi tach": [
                "Dùng keo dán da/giày chuyên dụng (UHU hoặc tương đương)",
                "Kẹp chặt và để khô tối thiểu 24h trước khi đi",
                "Nếu tách nhiều hoặc trong thời gian bảo hành 3 tháng: đổi hàng",
            ],
            "bi chan thuong do giay": [
                "Chọn đúng size (xem bảng hướng dẫn chọn size)",
                "Đi thêm đế lót bổ sung nếu chân dẹt hoặc cao vòm",
                "Tham khảo bài viết KB-011 về cách chọn size giày",
            ],
        },
    },
}