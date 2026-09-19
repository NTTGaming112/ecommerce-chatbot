"""Read-only tools for the Multi-Agent system."""
from app.tools.base import ReadTool, ToolResult, ToolError
from app.tools.mock_data import (
    MOCK_CUSTOMERS, MOCK_ORDERS, MOCK_SHIPPING, MOCK_PRODUCTS,
    MOCK_PRODUCTS_BY_ID, MOCK_STOCK, MOCK_PAYMENTS, MOCK_INVOICES,
    MOCK_KB_ARTICLES, RETURN_POLICY, TROUBLESHOOTING_GUIDES,
)

class GetCustomerProfile(ReadTool):
    def __init__(self):
        super().__init__("get_customer_profile", "Get customer profile by ID",
                         ["CustomerInfoAgent", "RefundAgent", "BillingAgent", "HumanHandoffAgent"])
    def validate_access(self, params, customer_id):
        if params.get("customer_id") and customer_id and params["customer_id"] != customer_id:
            raise PermissionError("Cannot access other customer data")
    def execute(self, params, customer_id=""):
        cid = params.get("customer_id", customer_id)
        c = MOCK_CUSTOMERS.get(cid)
        if not c:
            return ToolResult(success=False, error=ToolError("CustomerNotFound", f"Customer {cid} not found", "CUSTOMER_NOT_FOUND"))
        return ToolResult(success=True, data=c)

class GetOrder(ReadTool):
    def __init__(self):
        super().__init__("get_order", "Get order details", ["OrderAgent", "RefundAgent", "HumanHandoffAgent"])
    def validate_access(self, params, customer_id):
        o = MOCK_ORDERS.get(params.get("order_id", ""))
        if o and customer_id and o.get("customer_id") != customer_id:
            raise PermissionError("Cannot access other customer orders")
    def execute(self, params, customer_id=""):
        o = MOCK_ORDERS.get(params.get("order_id", ""))
        if not o:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {params.get('order_id')} not found", "ORDER_NOT_FOUND"))
        return ToolResult(success=True, data=o)

class GetShippingStatus(ReadTool):
    def __init__(self):
        super().__init__("get_shipping_status", "Get shipping tracking", ["OrderAgent"])
    def execute(self, params, customer_id=""):
        s = MOCK_SHIPPING.get(params.get("tracking_number", ""))
        if not s:
            return ToolResult(success=False, error=ToolError("TrackingNotFound", "Tracking not found", "TRACKING_NOT_FOUND"))
        return ToolResult(success=True, data=s)

class SearchProducts(ReadTool):
    def __init__(self):
        super().__init__("search_products", "Search products", ["ProductAgent", "KnowledgeBaseAgent"])

    def _extract_keywords(self, query):
        """Extract meaningful keywords from a natural language query."""
        import re
        # Common stop words to ignore
        stop_words = {'show', 'me', 'the', 'a', 'an', 'i', 'want', 'to', 'do', 'you',
                      'have', 'any', 'what', 'about', 'looking', 'for', 'find', 'search',
                      'get', 'give', 'see', 'can', 'could', 'please', 'like', 'some',
                      'need', 'buy', 'purchase', 'order', 'tim', 'cho', 'toi', 'co',
                      'san', 'pham', 'gia', 'ban', 'mua'}
        words = re.findall(r'[a-zA-ZÀ-ɏḀ-ỿ]+', query.lower())
        # Simple suffix stripping
        stemmed = []
        for w in words:
            if w in stop_words or len(w) <= 1:
                continue
            # Strip common English plurals
            if w.endswith('s') and len(w) > 3:
                w = w[:-1]
            stemmed.append(w)
        return stemmed

    def execute(self, params, customer_id=""):
        q = params.get("query", "").lower().strip()
        cat = params.get("category", "")
        r = MOCK_PRODUCTS

        if q:
            # Try exact substring match first
            exact = [p for p in r if q in p["name"].lower() or q in p.get("description", "").lower() or q in p["category"].lower()]
            if exact:
                r = exact
            else:
                # Fall back to keyword matching: ANY keyword must match
                keywords = self._extract_keywords(q)
                if keywords:
                    r = [p for p in r if any(
                        kw in p["name"].lower() or kw in p["category"].lower()
                        for kw in keywords
                    )]
                else:
                    r = []

        if cat:
            r = [p for p in r if p["category"] == cat]
        return ToolResult(success=True, data={"products": r, "total_count": len(r)})

class GetProductDetail(ReadTool):
    def __init__(self):
        super().__init__("get_product_detail", "Get product details", ["ProductAgent", "KnowledgeBaseAgent"])
    def execute(self, params, customer_id=""):
        p = MOCK_PRODUCTS_BY_ID.get(params.get("product_id", ""))
        if not p:
            return ToolResult(success=False, error=ToolError("ProductNotFound", "Product not found", "PRODUCT_NOT_FOUND"))
        stock = MOCK_STOCK.get(p["product_id"], {"in_stock": True, "variants": []})
        return ToolResult(success=True, data={**p, "stock": stock})

class CheckStock(ReadTool):
    def __init__(self):
        super().__init__("check_stock", "Check product inventory", ["ProductAgent", "RefundAgent"])
    def execute(self, params, customer_id=""):
        s = MOCK_STOCK.get(params.get("product_id", ""))
        if not s:
            s = {"product_id": params.get("product_id"), "in_stock": True, "variants": [{"color": "Default", "size": "M", "quantity": 10, "available": True}]}
        return ToolResult(success=True, data=s)

class CheckPaymentStatus(ReadTool):
    def __init__(self):
        super().__init__("check_payment_status", "Check payment status", ["BillingAgent", "HumanHandoffAgent"])
    def execute(self, params, customer_id=""):
        p = MOCK_PAYMENTS.get(params.get("order_id", ""))
        if not p:
            return ToolResult(success=False, error=ToolError("PaymentNotFound", "Payment not found", "PAYMENT_NOT_FOUND"))
        if customer_id and p.get("customer_id") != customer_id:
            return ToolResult(success=False, error=ToolError("PermissionDenied", "Access denied", "PERMISSION_DENIED"))
        return ToolResult(success=True, data=p)

class GetInvoice(ReadTool):
    def __init__(self):
        super().__init__("get_invoice", "Get invoice", ["BillingAgent", "HumanHandoffAgent"])
    def execute(self, params, customer_id=""):
        i = MOCK_INVOICES.get(params.get("order_id", ""))
        if not i:
            return ToolResult(success=False, error=ToolError("InvoiceNotFound", "Invoice not found", "INVOICE_NOT_FOUND"))
        return ToolResult(success=True, data=i)

class GetReturnPolicy(ReadTool):
    def __init__(self):
        super().__init__("get_return_policy", "Get return policy", ["OrderAgent", "RefundAgent", "KnowledgeBaseAgent"])
    def execute(self, params, customer_id=""):
        return ToolResult(success=True, data=RETURN_POLICY)

class SearchKnowledgeBase(ReadTool):
    def __init__(self):
        super().__init__("search_knowledge_base", "Search KB articles", ["KnowledgeBaseAgent", "TechSupportAgent", "ProductAgent", "HumanHandoffAgent"])
    def execute(self, params, customer_id=""):
        q = params.get("query", "").lower()
        cat = params.get("category", "")
        r = MOCK_KB_ARTICLES
        if cat and cat != "all":
            r = [a for a in r if a["category"] == cat]
        if q:
            r = [a for a in r if q in a["title"].lower() or q in a["content"].lower() or any(q in t for t in a.get("tags", []))]
        return ToolResult(success=True, data={"articles": r, "total_count": len(r)})

class GetTroubleshootingGuide(ReadTool):
    def __init__(self):
        super().__init__("get_troubleshooting_guide", "Get troubleshooting steps", ["TechSupportAgent"])
    def execute(self, params, customer_id=""):
        p = params.get("product_name", "").lower()
        for k, g in TROUBLESHOOTING_GUIDES.items():
            if k in p or p in g.get("product", "").lower():
                return ToolResult(success=True, data=g)
        return ToolResult(success=True, data={"product": p, "symptoms": {}, "message": "No guide found. Contact support."})

class GetCustomerTransactions(ReadTool):
    def __init__(self):
        super().__init__("get_customer_transactions", "Get customer orders", ["CustomerInfoAgent", "RefundAgent", "BillingAgent"])
    def validate_access(self, params, customer_id):
        if params.get("customer_id") and customer_id and params["customer_id"] != customer_id:
            raise PermissionError("Cannot access other customer transactions")
    def execute(self, params, customer_id=""):
        cid = params.get("customer_id", customer_id)
        orders = sorted([o for o in MOCK_ORDERS.values() if o["customer_id"] == cid], key=lambda x: x["created_at"], reverse=True)
        return ToolResult(success=True, data={"orders": orders, "total_count": len(orders)})

def register_all_read_tools(registry):
    for cls in [GetCustomerProfile, GetOrder, GetShippingStatus, SearchProducts,
                GetProductDetail, CheckStock, CheckPaymentStatus, GetInvoice,
                GetReturnPolicy, SearchKnowledgeBase, GetTroubleshootingGuide, GetCustomerTransactions]:
        registry.register(cls())
