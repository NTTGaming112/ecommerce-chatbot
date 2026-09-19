# Product Advisor Agent
from app.tools.registry import tool_registry

def search_products(query="", category=""):
    r = tool_registry.execute("search_products", {"query": query, "category": category}, agent="ProductAgent")
    return r.data if r.success else {"products": [], "total_count": 0}

def check_stock(pid):
    r = tool_registry.execute("check_stock", {"product_id": pid}, agent="ProductAgent")
    return r.data if r.success else {"in_stock": False, "variants": []}
