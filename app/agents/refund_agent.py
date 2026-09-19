# Refund and Return Agent
from app.tools.registry import tool_registry

def create_return_request(cid, oid, items, return_method="ship", refund_method="original_payment", confirmed=False):
    token = "confirmed" if confirmed else ""
    r = tool_registry.execute("create_return_request", {"customer_id": cid, "order_id": oid, "items": items, "return_method": return_method, "refund_method": refund_method, "confirmation_token": token}, agent="RefundAgent")
    if not r.success: return {"error": r.error.message, "needs_confirmation": "CONFIRMATION_REQUIRED" in (r.error.code if r.error else "")}
    return {"return_id": r.data["return_id"], "status": r.data["status"], "refund_amount": r.data["refund_amount"], "instructions": r.data["instructions"]}

def get_refund_status(refund_id=None, order_id=None):
    return {"refund_id": refund_id or "N/A", "status": "processing", "estimated_date": "2026-09-05"}
