# Router Agent - Intent classification and entity extraction
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

INTENT_PATTERNS = {
    "greeting": [r"^(xin\s+)?chao|hello|hi\b|hey|xin\s+chao"],
    "order_status": [
        r"don\s+hang|don\s+ORD|order\s+id|tracking|van\s+don|giao\s+hang",
        r"da\s+giao|den\s+dau|giao\s+chua|where\s+is\s+my\s+order|order\s+status",
        r"tinh\s+trang\s+don|check\s+order|ship\s+chua|ship\s+to\s+where",
        r"cong\s+ty\s+van\s+chuyen|carrier|ma\s+theo\s+doi",
    ],
    "return_request": [
        r"tra\s+hang|doi\s+hang|tra\s+lai|exchange|return\s+item|want\s+to\s+return",
        r"muon\s+tra|khong\s+thich|doi\s+size|doi\s+mau|tra\s+hoac\s+doi",
        r"lam\s+the\s+nao.*tra|cach\s+tra|huong\s+dan\s+tra",
        r"return\s+how|how\s+to\s+return|how\s+do\s+i\s+return",
    ],
    "refund": [
        r"hoan\s+tien|refund|hoan\s+la|tien\b.*\bhoan",
        r"lam\s+the\s+nao.*hoan|cach\s+hoan|huong\s+dan\s+hoan",
        r"how\s+to\s+refund|how\s+do\s+i\s+refund|re.fund",
    ],
    "product_query": [
        # Vietnamese product keywords
        r"tim\s+san\s+pham|mua\s+san\s+pham|gia\s+ban|bao\s+nhieu",
        r"liet\s+ke|xem\s+san\s+pham|tat\s+ca\s+san\s+pham|danh\s+sach",
        r"\bquan\b|\bgiay\b|\btui\b|\bdong\s+ho\b|\bvay\b",
        r"ao\s+jacket|quan\s+jean|ao\s+so\s+mi|vay\s+dam|giay\s+sneaker",
        r"may\s+loc|tui\s+xach|dong\s+ho",
        # English product keywords
        r"show\s+me|what\s+do\s+you\s+sell|got\s+any|products?\b|catalog",
        r"recommend|price\s+of|how\s+much|buy|want\s+to\s+buy|looking\s+for",
        r"do\s+you\s+have|search\s+product|shoes?|sneaker|bag|watch",
        r"dress|shirt|pants|jeans|filter|nuoc|ao\s+so\s+mi",
        r"your\s+product|list\s+your|all\s+product",
        # Category keywords
        r"\bnam\b.*\b(san\s+pham|product|ao|quan)\b",
        r"\bnu\b.*\b(san\s+pham|product|ao|vay)\b",
        r"gioi\s+tinh|\bnam\b|\bnu\b|phu\s+kien|gia\s+dung",
    ],
    "tech_support": [
        r"may\s+loc\s+nuoc|den\s+do\s+nhap\s+nay|khong\s+hoat\s+dong",
        r"troubleshoot|broken|not\s+working|malfunction|defect|\bloi\b",
        r"khong\s+biet|sua\s+chua|hu\s+nguyen|error\s+code|warning",
    ],
    "billing": [
        r"thanh\s+toan\s+bi\s+loi|thanh\s+toan.*\bloi\b|thanh\s+toan.*that\s+bai",
        r"bi\s+tru\s+tien|double\s+charge",
        r"tru\s+2\s+lan|mat\s+the|hoa\s+don\s+bi\s+loi|charged\s+twice",
        r"payment\s+error|overcharged|pay\s+bill|hoa\s+don|thanhtoan",
    ],
}

def classify_intent(message):
    msg = message.lower()
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, msg):
                scores[intent] = scores.get(intent, 0) + 1
    if not scores:
        return {"intent": "general", "confidence": 0.5}
    # Highest score wins; priority breaks ties (e.g. single ambiguous "loi" vs explicit return words)
    PRIORITY = ["billing", "tech_support", "return_request", "refund", "order_status", "product_query", "greeting"]
    best = max(scores, key=lambda intent: (scores[intent], -PRIORITY.index(intent)))
    return {"intent": best, "confidence": min(0.6 + scores[best] * 0.15, 0.95)}

def extract_entities(message, intent):
    e = {}
    m = re.search(r"ORD[-_]?(\d+)", message, re.I)
    if m: e["order_id"] = f"ORD-{m.group(1)}"
    if re.search(r"den\s+do|red\s+light", msg:=message.lower()): e["symptom"] = "den do nhap nay"
    if re.search(r"khong\s+ra\s+nuoc", msg): e["symptom"] = "khong ra nuoc"
    if re.search(r"tru\s+2\s+lan|double", msg): e["payment_issue"] = "double_charge"
    # Product name extraction
    product_keywords = [
        "ao jacket", "quan jean", "ao so mi", "vay dam", "giay sneaker",
        "may loc nuoc", "tui xach", "dong ho", "jacket", "sneaker",
        "jean", "shirt", "dress", "watch", "bag", "filter",
    ]
    for kw in product_keywords:
        if kw in msg:
            e["product_name"] = kw
            break
    return e

def determine_urgency(message, intent):
    msg = message.lower()
    if re.search(r"gap|urgent|cap\s+toc", msg): return "high"
    if intent in ("tech_support","billing","refund"): return "high"
    return "medium"

def generate_task_plan(intent, entities):
    plan = [{"agent":"CustomerInfoAgent","task":"verify_customer","depends_on":[]}]
    if intent == "order_status":
        plan += [{"agent":"OrderAgent","task":"check_order_status","depends_on":["verify_customer"]},{"agent":"KnowledgeBaseAgent","task":"generate_response","depends_on":["check_order_status"]}]
    elif intent == "return_request":
        plan += [{"agent":"OrderAgent","task":"check_return_eligibility","depends_on":["verify_customer"]},{"agent":"RefundAgent","task":"create_return_request","depends_on":["check_return_eligibility"],"confirmation":True},{"agent":"KnowledgeBaseAgent","task":"generate_response","depends_on":["create_return_request"]}]
    elif intent == "refund":
        plan += [{"agent":"OrderAgent","task":"search_orders","depends_on":["verify_customer"]},{"agent":"RefundAgent","task":"get_refund_status","depends_on":["search_orders"]},{"agent":"KnowledgeBaseAgent","task":"generate_response","depends_on":["get_refund_status"]}]
    elif intent == "product_query":
        plan += [{"agent":"ProductAgent","task":"search_products","depends_on":["verify_customer"]},{"agent":"KnowledgeBaseAgent","task":"generate_response","depends_on":["search_products"]}]
    elif intent == "tech_support":
        plan += [{"agent":"TechSupportAgent","task":"troubleshoot_issue","depends_on":["verify_customer"]},{"agent":"KnowledgeBaseAgent","task":"generate_response","depends_on":["troubleshoot_issue"]}]
    elif intent == "billing":
        plan += [{"agent":"BillingAgent","task":"check_payment","depends_on":["verify_customer"]},{"agent":"KnowledgeBaseAgent","task":"generate_response","depends_on":["check_payment"]}]
    else:
        plan += [{"agent":"KnowledgeBaseAgent","task":"generate_response","depends_on":["verify_customer"]}]
    return plan
