# Order Management Agent
from app.tools.registry import tool_registry

def check_order_status(cid, oid):
    r = tool_registry.execute("get_order", {"order_id": oid}, agent="OrderAgent", customer_id=cid)
    if not r.success: return {"error": r.error.message}
    o = r.data
    res = {"order_id": o["order_id"], "status": o["status"], "items": o.get("items",[]), "total": o.get("total",0)}
    if o.get("tracking_number"):
        sr = tool_registry.execute("get_shipping_status", {"tracking_number": o["tracking_number"]}, agent="OrderAgent")
        if sr.success: res["tracking"] = sr.data
    return res

def check_return_eligibility(cid, oid, items=None):
    r = tool_registry.execute("get_order", {"order_id": oid}, agent="OrderAgent", customer_id=cid)
    if not r.success: return {"eligible": False, "error": r.error.message}
    o = r.data
    if o["status"] == "cancelled": return {"eligible": False, "reason": "Order already cancelled"}
    if o["status"] == "delivered": return {"eligible": True, "total_refund": o["total"], "items": o.get("items",[])}
    return {"eligible": o["status"] not in ("shipped", "delivered"), "reason": f"Status: {o['status']}"}

def search_orders(cid):
    r = tool_registry.execute("get_customer_transactions", {"customer_id": cid}, agent="OrderAgent", customer_id=cid)
    return r.data if r.success else {"orders": [], "total_count": 0}
