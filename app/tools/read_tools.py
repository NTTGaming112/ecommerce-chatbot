"""Read-only tools for the Multi-Agent system backed by SQLite Database."""
import logging
from app.tools.base import ReadTool, ToolResult, ToolError
from app.services.database import db_service
from app.tools.mock_data import (
    MOCK_INVOICES, MOCK_KB_ARTICLES, RETURN_POLICY, TROUBLESHOOTING_GUIDES,
)

logger = logging.getLogger(__name__)

class GetCustomerProfile(ReadTool):
    def __init__(self):
        super().__init__("get_customer_profile", "Get customer profile by ID",
                         ["CustomerInfoAgent", "RefundAgent", "BillingAgent", "HumanHandoffAgent"])
    def validate_access(self, params, customer_id):
        if params.get("customer_id") and customer_id and params["customer_id"] != customer_id:
            raise PermissionError("Cannot access other customer data")
    def execute(self, params, customer_id=""):
        cid = params.get("customer_id", customer_id)
        c = db_service.get_customer(cid)
        if not c:
            return ToolResult(success=False, error=ToolError("CustomerNotFound", f"Customer {cid} not found", "CUSTOMER_NOT_FOUND"))
        return ToolResult(success=True, data=c)

class GetOrder(ReadTool):
    def __init__(self):
        super().__init__("get_order", "Get order details", ["OrderAgent", "RefundAgent", "HumanHandoffAgent"])
    def validate_access(self, params, customer_id):
        o = db_service.get_order(params.get("order_id", ""))
        if o and customer_id and o.get("customer_id") != customer_id:
            raise PermissionError("Cannot access other customer orders")
    def execute(self, params, customer_id=""):
        oid = params.get("order_id", "")
        o = db_service.get_order(oid)
        if not o:
            return ToolResult(success=False, error=ToolError("OrderNotFound", f"Order {oid} not found", "ORDER_NOT_FOUND"))
        return ToolResult(success=True, data=o)

class GetShippingStatus(ReadTool):
    def __init__(self):
        super().__init__("get_shipping_status", "Get shipping tracking", ["OrderAgent"])
    def execute(self, params, customer_id=""):
        trk = params.get("tracking_number", "")
        s = db_service.get_shipping(trk)
        if not s:
            return ToolResult(success=False, error=ToolError("TrackingNotFound", "Tracking not found", "TRACKING_NOT_FOUND"))
        return ToolResult(success=True, data=s)

class SearchProducts(ReadTool):
    def __init__(self):
        super().__init__("search_products", "Search products", ["ProductAgent", "KnowledgeBaseAgent"])

    def execute(self, params, customer_id=""):
        q = params.get("query", "").strip()
        cat = params.get("category", "")
        products = db_service.search_products(query=q, category=cat if cat else None, limit=20)
        return ToolResult(success=True, data={"products": products, "total_count": len(products)})

class GetProductDetail(ReadTool):
    def __init__(self):
        super().__init__("get_product_detail", "Get product details", ["ProductAgent", "KnowledgeBaseAgent"])
    def execute(self, params, customer_id=""):
        pid = params.get("product_id", "")
        p = db_service.get_product(pid)
        if not p:
            return ToolResult(success=False, error=ToolError("ProductNotFound", "Product not found", "PRODUCT_NOT_FOUND"))
        stock = p.get("stock_info", {"in_stock": True, "variants": []})
        return ToolResult(success=True, data={**p, "stock": stock})

class CheckStock(ReadTool):
    def __init__(self):
        super().__init__("check_stock", "Check product inventory", ["ProductAgent", "RefundAgent"])
    def execute(self, params, customer_id=""):
        pid = params.get("product_id", "")
        p = db_service.get_product(pid)
        if p and p.get("stock_info"):
            return ToolResult(success=True, data=p["stock_info"])
        s = {"product_id": pid, "in_stock": True, "variants": [{"color": "Default", "size": "M", "quantity": 10, "available": True}]}
        return ToolResult(success=True, data=s)

class CheckPaymentStatus(ReadTool):
    def __init__(self):
        super().__init__("check_payment_status", "Check payment status", ["BillingAgent", "HumanHandoffAgent"])
    def execute(self, params, customer_id=""):
        oid = params.get("order_id", "")
        p = db_service.get_payment_by_order(oid)
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
        super().__init__("search_knowledge_base", "Search KB articles (policies, guides, regulations, FAQ)",
                         ["KnowledgeBaseAgent", "TechSupportAgent", "ProductAgent", "HumanHandoffAgent"])

    def execute(self, params, customer_id=""):
        q = params.get("query", "").strip()
        cat = params.get("category", "")
        articles = db_service.search_kb_articles(query=q, category=cat if cat and cat != "all" else None, limit=10)
        return ToolResult(success=True, data={"articles": articles, "total_count": len(articles)})

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
        orders = db_service.get_orders_by_customer(cid)
        return ToolResult(success=True, data={"orders": orders, "total_count": len(orders)})

def register_all_read_tools(registry):
    for cls in [GetCustomerProfile, GetOrder, GetShippingStatus, SearchProducts,
                GetProductDetail, CheckStock, CheckPaymentStatus, GetInvoice,
                GetReturnPolicy, SearchKnowledgeBase, GetTroubleshootingGuide, GetCustomerTransactions]:
        registry.register(cls())
