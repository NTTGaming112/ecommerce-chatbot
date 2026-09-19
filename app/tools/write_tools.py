"""Write/Action tools for the Multi-Agent system backed by SQLite Database."""
import logging
from app.tools.base import WriteTool, ToolResult, ToolError
from app.services.database import db_service

logger = logging.getLogger(__name__)

_refund_counter = 200

class CreateReturnRequest(WriteTool):
    def __init__(self):
        super().__init__("create_return_request", "Create a return request",
                         ["RefundAgent"], requires_confirmation=True)
    def execute(self, params, customer_id=""):
        if not params.get("confirmation_token"):
            return ToolResult(success=False, error=ToolError("ConfirmationRequired", "Customer confirmation required", "CONFIRMATION_REQUIRED"))
        oid = params.get("order_id", "")
        order = db_service.get_order(oid)
        if not order:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {oid} not found", "ORDER_NOT_FOUND"))
        if order.get("status") == "cancelled":
            return ToolResult(success=False, error=ToolError("OrderCancelled", "Order already cancelled", "ORDER_CANCELLED"))
        
        refund_amount = sum(item.get("price", 0) * item.get("qty", 1) for item in params.get("items", []))
        if not refund_amount:
            refund_amount = order.get("total", 0)
            
        instructions = "In label gui hang tai kho nhan" if params.get("return_method") == "ship" else "Mang den cua hang"
        reason = params.get("reason", "")
        
        ret_data = db_service.create_return(
            order_id=oid,
            customer_id=order.get("customer_id", customer_id),
            refund_amount=refund_amount,
            instructions=instructions,
            reason=reason
        )
        return ToolResult(success=True, data=ret_data)

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
        order = db_service.get_order(oid)
        if not order:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {oid} not found", "ORDER_NOT_FOUND"))
        if order.get("status") in ("shipped", "delivered"):
            return ToolResult(success=False, error=ToolError("CannotCancel", "Cannot cancel shipped/delivered order", "CANNOT_CANCEL"))
        
        updated = db_service.cancel_order(oid, reason=params.get("reason", "Khách yêu cầu hủy"))
        return ToolResult(success=True, data={
            "cancelled": True, "order_id": oid,
            "refund_amount": updated.get("total", 0) if updated else order.get("total", 0),
            "refund_eta": "3-5 ngay lam viec",
        })

class UpdateOrderAddress(WriteTool):
    def __init__(self):
        super().__init__("update_order_address", "Update shipping address",
                         ["OrderAgent"], requires_confirmation=True)
    def execute(self, params, customer_id=""):
        if not params.get("confirmation_token"):
            return ToolResult(success=False, error=ToolError("ConfirmationRequired", "Confirmation required", "CONFIRMATION_REQUIRED"))
        oid = params.get("order_id", "")
        order = db_service.get_order(oid)
        if not order:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {oid} not found", "ORDER_NOT_FOUND"))
        if order.get("status") in ("shipped", "delivered"):
            return ToolResult(success=False, error=ToolError("CannotUpdate", "Cannot update shipped order", "CANNOT_UPDATE"))
        
        new_address = params.get("new_address", {})
        db_service.update_order_address(oid, new_address)
        return ToolResult(success=True, data={"updated": True, "order_id": oid, "new_address": new_address})

class CreateSupportTicket(WriteTool):
    def __init__(self):
        super().__init__("create_support_ticket", "Create a support ticket",
                         ["HumanHandoffAgent", "TechSupportAgent"], requires_confirmation=False)
    def execute(self, params, customer_id=""):
        cid = params.get("customer_id", customer_id)
        subject = params.get("issue_summary", params.get("symptom", "Yêu cầu hỗ trợ kỹ thuật"))
        priority = params.get("priority", "medium")
        ticket = db_service.create_ticket(customer_id=cid, subject=subject, priority=priority)
        return ToolResult(success=True, data={
            "ticket_id": ticket["ticket_id"], "status": "open",
            "assigned_to": params.get("required_skill", "CSKH Team"),
            "estimated_response_time": "5 phut" if priority == "urgent" else "30 phut",
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
