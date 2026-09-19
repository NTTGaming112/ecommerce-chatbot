# Human Handoff Agent
from app.tools.registry import tool_registry

def evaluate_handoff(reason, confidence, retry_count, max_retries):
    return {"handoff_recommended": confidence < 0.3 or retry_count >= max_retries, "reason": reason}

def execute_handoff(cid, summary, skill="CSKH", urgency="medium"):
    r1 = tool_registry.execute("create_support_ticket", {"customer_id": cid, "subject": "Customer handoff", "description": summary, "priority": urgency, "required_skill": skill}, agent="HumanHandoffAgent")
    if not r1.success: return {"error": r1.error.message}
    tool_registry.execute("notify_human_agent", {"ticket_id": r1.data["ticket_id"], "urgency": urgency, "message": summary}, agent="HumanHandoffAgent")
    tid = r1.data["ticket_id"]
    return {"ticket_id": tid, "assigned_to": r1.data.get("assigned_to","CSKH"), "estimated_wait_time": r1.data.get("estimated_response_time","30 phut"), "handoff_message": "Da tao ticket %s. Nhan vien se lien he som." % tid}
