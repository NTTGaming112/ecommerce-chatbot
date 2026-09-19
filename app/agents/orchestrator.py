# Orchestrator - Coordinates all agents
import logging
from typing import Dict, Any
from app.agents.router_agent import classify_intent, extract_entities, determine_urgency, generate_task_plan
from app.agents import customer_info_agent, order_agent, product_agent, refund_agent
from app.agents import tech_support_agent, billing_agent, knowledge_base_agent, human_handoff_agent

logger = logging.getLogger(__name__)

def process_message(customer_id, message, history=None):
    """Main orchestrator entry point."""
    state = {"customer_id": customer_id, "message": message, "results": {}, "actions": []}
    
    # Step 1: Router - classify intent
    intent_result = classify_intent(message)
    state["intent"] = intent_result["intent"]
    state["confidence"] = intent_result["confidence"]
    
    # Step 2: Extract entities
    entities = extract_entities(message, intent_result["intent"])
    state["entities"] = entities
    
    # Step 3: Determine urgency
    urgency = determine_urgency(message, intent_result["intent"])
    state["urgency"] = urgency
    
    # Step 4: Generate task plan
    task_plan = generate_task_plan(intent_result["intent"], entities)
    state["task_plan"] = task_plan
    
    # Step 5: Execute tasks in order
    for task in task_plan:
        agent_name = task["agent"]
        task_name = task["task"]
        try:
            result = _execute_task(agent_name, task_name, customer_id, entities, state)
            state["results"][task_name] = result
            state["actions"].append(f"{agent_name}.{task_name}")
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
            state["results"][task_name] = {"error": str(e)}
            state.setdefault("errors", []).append({"task": task_name, "error": str(e)})
    
    # Step 6: Generate final response
    response = knowledge_base_agent.generate_response(message, state["results"], state["intent"])
    state["final_response"] = response
    
    return state

def _execute_task(agent, task, cid, entities, state):
    """Execute a single task by the appropriate agent."""
    if agent == "CustomerInfoAgent" and task == "verify_customer":
        return customer_info_agent.verify_customer(cid)
    
    elif agent == "OrderAgent" and task == "check_order_status":
        oid = entities.get("order_id", "")
        if not oid:
            txns = order_agent.search_orders(cid)
            orders = txns.get("orders", [])
            if orders:
                oid = orders[0]["order_id"]
        if not oid:
            return {"status": "unknown", "message": "Please provide an order ID (e.g., ORD-12345)"}
        return order_agent.check_order_status(cid, oid)
    
    elif agent == "OrderAgent" and task == "check_return_eligibility":
        oid = entities.get("order_id", "")
        return order_agent.check_return_eligibility(cid, oid) if oid else {"error": "No order ID"}
    
    elif agent == "OrderAgent" and task == "search_orders":
        return order_agent.search_orders(cid)
    
    elif agent == "RefundAgent" and task == "create_return_request":
        oid = entities.get("order_id", "")
        items = entities.get("items", [{"product_id": "unknown", "qty": 1, "price": 0}])
        return refund_agent.create_return_request(cid, oid, items, confirmed=True)
    
    elif agent == "RefundAgent" and task == "get_refund_status":
        return refund_agent.get_refund_status(order_id=entities.get("order_id"))
    
    elif agent == "ProductAgent" and task == "search_products":
        query = entities.get("product_name", "") if isinstance(entities, dict) else ""
        msg = state.get("message", "").lower()
        # If generic request ("show all", "list products", "xem san pham"), search with empty query
        generic_patterns = ['list', 'all', 'show', 'xem', 'liet', 'tat ca', 'danh sach', 'ban co', 'your product', 'product']
        is_generic = any(p in msg for p in generic_patterns) and not query
        if is_generic:
            return product_agent.search_products(query="")
        return product_agent.search_products(query=msg)
    
    elif agent == "TechSupportAgent" and task == "troubleshoot_issue":
        pname = entities.get("product_name", "")
        symptom = entities.get("symptom", "")
        return tech_support_agent.troubleshoot_issue(cid, product_name=pname, symptom=symptom)
    
    elif agent == "BillingAgent" and task == "check_payment":
        oid = entities.get("order_id", "")
        if not oid:
            return {"message": "Please provide an order ID to check payment status"}
        return billing_agent.check_payment(cid, order_id=oid)
    
    elif agent == "KnowledgeBaseAgent" and task == "generate_response":
        # Search KB for relevant articles
        kb_result = knowledge_base_agent.search_kb(query=state.get("message", ""))
        return {"kb": kb_result}
    
    return {"error": f"Unknown task: {agent}.{task}"}
