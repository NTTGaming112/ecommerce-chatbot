# Customer Information Agent
from app.tools.registry import tool_registry

def verify_customer(cid):
    r = tool_registry.execute("get_customer_profile", {"customer_id": cid}, agent="CustomerInfoAgent", customer_id=cid)
    if not r.success:
        # For unknown customers, return a default profile (demo mode)
        return {"verified": True, "customer": {"customer_id": cid, "name": "Guest User", "loyalty_tier": "bronze"}, "loyalty_tier": "bronze", "is_demo": True}
    return {"verified": True, "customer": r.data, "loyalty_tier": r.data.get("loyalty_tier","bronze")}

def get_customer_transactions(cid):
    r = tool_registry.execute("get_customer_transactions", {"customer_id": cid}, agent="CustomerInfoAgent", customer_id=cid)
    return r.data if r.success else {"orders": [], "total_count": 0}
