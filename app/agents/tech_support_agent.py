# Technical Support Agent
from app.tools.registry import tool_registry

def troubleshoot_issue(cid, product_name="", symptom=""):
    guide = {}
    r = tool_registry.execute("get_troubleshooting_guide", {"product_name": product_name}, agent="TechSupportAgent")
    if r.success: guide = r.data
    kb = tool_registry.execute("search_knowledge_base", {"query": f"{product_name} {symptom}"}, agent="TechSupportAgent")
    articles = kb.data.get("articles", []) if kb.success else []
    steps = guide.get("symptoms", {}).get(symptom, []) if guide else []
    return {"product": guide.get("product", product_name), "symptom": symptom, "troubleshooting_steps": steps, "kb_articles": [{"id": a["id"], "title": a["title"]} for a in articles[:3]], "is_resolved": False, "escalation_needed": len(steps) == 0}
