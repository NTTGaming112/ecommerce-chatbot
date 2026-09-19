# Billing and Payment Agent
from app.tools.registry import tool_registry

def check_payment(cid, order_id=None):
    if not order_id: return {"error": "Order ID required"}
    r = tool_registry.execute("check_payment_status", {"order_id": order_id}, agent="BillingAgent", customer_id=cid)
    if not r.success: return {"error": r.error.message}
    return {"payment_id": r.data["payment_id"], "status": r.data["status"], "amount": r.data["amount"], "method": r.data.get("method","N/A")}

def get_invoice(cid, oid):
    r = tool_registry.execute("get_invoice", {"order_id": oid}, agent="BillingAgent", customer_id=cid)
    return r.data if r.success else {"error": "Invoice not found"}
