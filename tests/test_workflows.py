"""End-to-end tests for Multi-Agent Customer Support System."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestWorkflow1_OrderStatus:
    """Workflow 1: Customer asks about order status with real-world tracking."""

    def test_order_status_with_tracking(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don hang ORD-12345 cua toi den dau roi?"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "order_status"
        assert data["confidence"] > 0.5
        assert any("OrderAgent" in a for a in data["actions_taken"])
        # Bot phải trả lời chứa mã đơn và thông tin vận chuyển
        ans = data["answer"].lower()
        assert "ord-12345" in ans or "shipped" in ans or "đang giao" in ans
        assert "trk-789" in ans or "ghn" in ans or "vận chuyển" in ans

    def test_order_status_delivered(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don ORD-12346 da giao chua?"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "order_status"
        ans = data["answer"].lower()
        assert "ord-12346" in ans or "giao" in ans or "delivered" in ans

    def test_order_not_found(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don hang ORD-99999 cua toi?"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "order_status"
        ans = data["answer"].lower()
        assert "không tìm thấy" in ans or "khong tim thay" in ans or "ord-99999" in ans


class TestWorkflow2_ReturnExchange:
    """Workflow 2: Customer wants to return/exchange a product (requires confirmation flow)."""

    def test_return_request_trigger_confirmation(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Toi muon tra lai ao jacket don ORD-12346, bi loi duong may"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] in ("return_request", "refund")
        assert any("OrderAgent" in a or "RefundAgent" in a for a in data["actions_taken"])
        assert data["needs_confirmation"] is True
        assert data["session_id"] != ""

    def test_return_eligibility_inquiry(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don ORD-12346 co the tra hang duoc khong?"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] in ("return_request", "refund", "order_status")
        assert any("OrderAgent" in a or "RefundAgent" in a for a in data["actions_taken"])


class TestWorkflow3_Refund:
    """Workflow 3: Customer requests or inquires about refund status."""

    def test_refund_status_inquiry(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Toi da tra hang 2 tuan roi nhung chua nhan duoc tien hoan"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] in ("refund", "return_request")
        assert any("RefundAgent" in a or "OrderAgent" in a for a in data["actions_taken"])


class TestWorkflow4_PaymentIssue:
    """Workflow 4: Customer has a payment error (double charge or failed)."""

    def test_double_charge(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Toi bi tru tien 2 lan cho don ORD-12345"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "billing"
        assert any("BillingAgent" in a for a in data["actions_taken"])
        ans = data["answer"].lower()
        assert "ord-12345" in ans or "thanh toán" in ans or "hoàn" in ans

    def test_payment_failed(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_002",
            "message": "Thanh toan don ORD-20002 bi loi"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "billing"
        assert any("BillingAgent" in a for a in data["actions_taken"])


class TestWorkflow5_TechSupport:
    """Workflow 5: Technical support and troubleshooting."""

    def test_troubleshoot_water_purifier(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "May loc nuoc bi loi, den do nhap nay"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] in ("tech_support", "return_request")
        assert any("TechSupportAgent" in a for a in data["actions_taken"])
        ans = data["answer"].lower()
        assert "nước" in ans or "điện" in ans or "van" in ans or "khắc phục" in ans

    def test_general_inquiry(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Xin chao"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "greeting"
        assert len(data["answer"]) > 5


class TestAPIEndpoints:
    """Test basic API endpoints."""

    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "AI Customer Support" in r.json()["message"]

    def test_health(self):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"

    def test_tools_list(self):
        r = client.get("/api/v1/tools")
        assert r.status_code == 200
        tools = r.json()["tools"]
        assert len(tools) >= 12
        tool_names = [t["name"] for t in tools]
        assert "get_customer_profile" in tool_names
        assert "create_return_request" in tool_names

    def test_chat_invalid_customer(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "nonexistent",
            "message": "Hello"
        })
        assert r.status_code == 200

    def test_chat_empty_message(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": ""
        })
        assert r.status_code == 422


class TestSecurityAndConfirmation:
    """Test security isolation and write action confirmations."""

    def test_customer_data_isolation(self):
        from app.tools import tool_registry
        r = tool_registry.execute("get_order", {"order_id": "ORD-20001"},
                                  agent="OrderAgent", customer_id="cust_001")
        assert not r.success
        assert "PermissionDenied" in r.error.error_type or "permission" in r.error.message.lower()

    def test_write_tool_requires_confirmation(self):
        from app.tools import tool_registry
        r = tool_registry.execute("create_return_request", {
            "customer_id": "cust_001", "order_id": "ORD-12346",
            "items": [{"product_id": "prod_002", "qty": 1}],
            "return_method": "ship", "refund_method": "original_payment"
        }, agent="RefundAgent")
        assert not r.success
        assert "ConfirmationRequired" in r.error.error_type


class TestEcommerceEndpoints:
    """Test REST API endpoints serving data to the Frontend UI."""

    def test_get_customers(self):
        r = client.get("/api/v1/customers")
        assert r.status_code == 200
        data = r.json()
        assert "customers" in data
        assert len(data["customers"]) >= 5
        first = data["customers"][0]
        assert "customer_id" in first
        assert "name" in first
        assert "loyalty_tier" in first

    def test_get_products(self):
        r = client.get("/api/v1/products")
        assert r.status_code == 200
        data = r.json()
        assert "products" in data
        assert len(data["products"]) >= 10

    def test_get_customer_orders(self):
        r = client.get("/api/v1/orders/cust_001")
        assert r.status_code == 200
        data = r.json()
        assert "orders" in data
        assert isinstance(data["orders"], list)

    def test_get_kb_articles(self):
        r = client.get("/api/v1/kb-articles")
        assert r.status_code == 200
        data = r.json()
        assert "articles" in data
        assert len(data["articles"]) >= 5

    def test_get_troubleshooting_guides(self):
        r = client.get("/api/v1/troubleshooting")
        assert r.status_code == 200
        data = r.json()
        assert "guides" in data
        assert len(data["guides"]) >= 1
