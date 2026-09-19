"""End-to-end tests for all 5 customer support workflows."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestWorkflow1_OrderStatus:
    """Workflow 1: Customer asks about order status."""

    def test_order_status_with_tracking(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don hang ORD-12345 cua toi den dau roi?"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "order_status"
        assert data["confidence"] > 0.5
        assert "CustomerInfoAgent" in str(data["actions_taken"])
        assert "OrderAgent" in str(data["actions_taken"])
        assert "ORD-12345" in data["answer"] or "shipped" in data["answer"]
        assert "TRK-789" in data["answer"] or "GHN" in data["answer"]

    def test_order_status_delivered(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don ORD-12346 da giao chua?"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "order_status"
        assert "giao thanh cong" in data["answer"].lower()

    def test_order_not_found(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don hang ORD-99999 cua toi?"
        })
        assert r.status_code == 200
        data = r.json()
        assert "khong tim thay" in data["answer"].lower()


class TestWorkflow2_ReturnExchange:
    """Workflow 2: Customer wants to return/exchange a product."""

    def test_return_request(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Toi muon tra lai ao jacket ORD-12346, bi loi duong may"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] in ("return_request", "refund")
        assert "CustomerInfoAgent" in str(data["actions_taken"])
        assert "OrderAgent" in str(data["actions_taken"])
        assert "RefundAgent" in str(data["actions_taken"])

    def test_return_eligibility(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Don ORD-12346 co the tra hang duoc khong?"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "return_request"


class TestWorkflow3_Refund:
    """Workflow 3: Customer requests a refund."""

    def test_refund_status_inquiry(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Toi da tra hang 2 tuan roi nhung chua nhan duoc tien hoan"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] in ("refund", "return_request")


class TestWorkflow4_PaymentIssue:
    """Workflow 4: Customer has a payment error (double charge)."""

    def test_double_charge(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Toi bi tru tien 2 lan cho don ORD-12345"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "billing"
        assert "BillingAgent" in str(data["actions_taken"])
        assert "CustomerInfoAgent" in str(data["actions_taken"])

    def test_payment_failed(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_002",
            "message": "Thanh toan don ORD-20002 bi loi"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "billing"


class TestWorkflow5_TechSupport:
    """Workflow 5: Technical support with escalation."""

    def test_troubleshoot_water_purifier(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "May loc nuoc bi loi, den do nhap nay"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] in ("tech_support", "return_request")
        assert "TechSupportAgent" in str(data["actions_taken"]) or "OrderAgent" in str(data["actions_taken"])

    def test_general_inquiry(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": "Xin chao"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "greeting"


class TestAPIEndpoints:
    """Test basic API functionality."""

    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "AI Customer Support" in r.json()["message"]

    def test_health(self):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["agents"] == 10
        assert data["tools"] == 18

    def test_tools_list(self):
        r = client.get("/api/v1/tools")
        assert r.status_code == 200
        tools = r.json()["tools"]
        assert len(tools) == 18
        tool_names = [t["name"] for t in tools]
        assert "get_customer_profile" in tool_names
        assert "create_return_request" in tool_names

    def test_chat_invalid_customer(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "nonexistent",
            "message": "Hello"
        })
        assert r.status_code == 200  # Should still work, just no customer data

    def test_chat_empty_message(self):
        r = client.post("/api/v1/chat", json={
            "customer_id": "cust_001",
            "message": ""
        })
        assert r.status_code == 422  # Validation error


class TestSecurity:
    """Test security features."""

    def test_customer_data_isolation(self):
        # cust_001 should not access cust_002 orders
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
