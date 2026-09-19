"""Write/Action tools for the Multi-Agent system."""
import logging
import uuid

from app.tools.base import WriteTool, ToolResult, ToolError
from app.tools.mock_data import MOCK_ORDERS, MOCK_PAYMENTS

logger = logging.getLogger(__name__)

# Mutable counters for mock data
_return_counter = 100
_refund_counter = 200
_ticket_counter = 500

class CreateReturnRequest(WriteTool):
    def __init__(self):
        super().__init__("create_return_request", "Create a return request",
                         ["RefundAgent"], requires_confirmation=True)
    def execute(self, params, customer_id=""):
        global _return_counter
        if not params.get("confirmation_token"):
            return ToolResult(success=False, error=ToolError("ConfirmationRequired", "Customer confirmation required", "CONFIRMATION_REQUIRED"))
        oid = params.get("order_id", "")
        order = MOCK_ORDERS.get(oid)
        if not order:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {oid} not found", "ORDER_NOT_FOUND"))
        if order.get("status") == "cancelled":
            return ToolResult(success=False, error=ToolError("OrderCancelled", "Order already cancelled", "ORDER_CANCELLED"))
        _return_counter += 1
        refund_amount = sum(item.get("price", 0) * item.get("qty", 1) for item in params.get("items", []))
        if not refund_amount:
            refund_amount = order.get("total", 0)
        status = "pending_approval" if refund_amount > 500 * 1000 else "approved"
        return ToolResult(success=True, data={
            "return_id": f"RET-{_return_counter}", "status": status,
            "refund_amount": refund_amount, "estimated_refund_date": "2026-09-01",
            "instructions": "In label gui hang tai kho nhan" if params.get("return_method") == "ship" else "Mang den cua hang",
        })

class CreateRefundRequest(WriteTool):
    def __init__(self):
        super().__init__("create_refund_request", "Create a refund request",
                         ["RefundAgent"], requires_confirmation=True)
    def execute(self, params, customer_id=""):
        global _refund_counter
        if not params.get("confirmation_token"):
            return ToolResult(success=False, error=ToolError("ConfirmationRequired", "Confirmation required", "CONFIRMATION_REQUIRED"))
        amount = params.get("amount", 0)
        if amount > 500 * 1000:
            return ToolResult(success=False, error=ToolError("RequiresHumanApproval", f"Refund {amount} requires human approval", "HUMAN_APPROVAL_REQUIRED"))
        _refund_counter += 1
        return ToolResult(success=True, data={
            "refund_id": f"REF-{_refund_counter}", "amount": amount,
            "status": "processing", "estimated_date": "2026-09-05",
        })

class CancelOrder(WriteTool):
    def __init__(self):
        super().__init__("cancel_order", "Cancel an order",
                         ["OrderAgent"], requires_confirmation=True)
    def execute(self, params, customer_id=""):
        if not params.get("confirmation_token"):
            return ToolResult(success=False, error=ToolError("ConfirmationRequired", "Confirmation required", "CONFIRMATION_REQUIRED"))
        oid = params.get("order_id", "")
        order = MOCK_ORDERS.get(oid)
        if not order:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {oid} not found", "ORDER_NOT_FOUND"))
        if order.get("status") in ("shipped", "delivered"):
            return ToolResult(success=False, error=ToolError("CannotCancel", "Cannot cancel shipped/delivered order", "CANNOT_CANCEL"))
        order["status"] = "cancelled"
        return ToolResult(success=True, data={
            "cancelled": True, "order_id": oid,
            "refund_amount": order.get("total", 0), "refund_eta": "3-5 ngay lam viec",
        })

class UpdateOrderAddress(WriteTool):
    def __init__(self):
        super().__init__("update_order_address", "Update shipping address",
                         ["OrderAgent"], requires_confirmation=True)
    def execute(self, params, customer_id=""):
        if not params.get("confirmation_token"):
            return ToolResult(success=False, error=ToolError("ConfirmationRequired", "Confirmation required", "CONFIRMATION_REQUIRED"))
        oid = params.get("order_id", "")
        order = MOCK_ORDERS.get(oid)
        if not order:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {oid} not found", "ORDER_NOT_FOUND"))
        if order.get("status") in ("shipped", "delivered"):
            return ToolResult(success=False, error=ToolError("CannotUpdate", "Cannot update shipped order", "CANNOT_UPDATE"))
        order["shipping_address"] = params.get("new_address", {})
        return ToolResult(success=True, data={"updated": True, "order_id": oid, "new_address": params.get("new_address")})

class CreateSupportTicket(WriteTool):
    def __init__(self):
        super().__init__("create_support_ticket", "Create a support ticket",
                         ["HumanHandoffAgent", "TechSupportAgent"], requires_confirmation=False)
    def execute(self, params, customer_id=""):
        global _ticket_counter
        _ticket_counter += 1
        return ToolResult(success=True, data={
            "ticket_id": f"TKT-{_ticket_counter}", "status": "open",
            "assigned_to": params.get("required_skill", "CSKH Team"),
            "estimated_response_time": "5 phut" if params.get("priority") == "urgent" else "30 phut",
        })

class NotifyHumanAgent(WriteTool):
    def __init__(self):
        super().__init__("notify_human_agent", "Notify a human agent",
                         ["HumanHandoffAgent"], requires_confirmation=False)
    def execute(self, params, customer_id=""):
        logger.info("Human agent notified: ticket=%s urgency=%s", params.get("ticket_id"), params.get("urgency"))
        return ToolResult(success=True, data={"notified": True, "channel": "dashboard"})

def register_all_write_tools(registry):
    for cls in [CreateReturnRequest, CreateRefundRequest, CancelOrder,
                UpdateOrderAddress, CreateSupportTicket, NotifyHumanAgent]:
        registry.register(cls())
