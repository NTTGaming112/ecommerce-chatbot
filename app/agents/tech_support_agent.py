# Technical Support Agent
from app.tools.registry import tool_registry

def troubleshoot_issue(cid, product_name="", symptom=""):
    guide = {}
    r = tool_registry.execute("get_troubleshooting_guide", {"product_name": product_name}, agent="TechSupportAgent")
    if r.success: guide = r.data
    kb = tool_registry.execute("search_knowledge_base", {"query": f"{product_name} {symptom}"}, agent="TechSupportAgent")
    articles = kb.data.get("articles", []) if kb.success else []
    steps = []
    if guide and isinstance(guide.get("symptoms"), dict):
        symptoms_dict = guide["symptoms"]
        if symptom in symptoms_dict:
            steps = symptoms_dict[symptom]
        else:
            s_clean = symptom.lower().strip()
            for k, v in symptoms_dict.items():
                if k in s_clean or s_clean in k or any(w in s_clean for w in k.split() if len(w) > 2):
                    steps = v
                    break
    return {
        "product": guide.get("product", product_name),
        "symptom": symptom,
        "troubleshooting_steps": steps,
        "kb_articles": [{"id": a.get("id", a.get("article_id", "")), "title": a.get("title", "")} for a in articles[:3]],
        "is_resolved": False,
        "escalation_needed": len(steps) == 0,
    }
