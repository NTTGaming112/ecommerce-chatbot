"""Domain Fetcher - Coordinates Domain Data Agents to fetch structured real-world context for LLM grounding."""
import logging
from typing import Dict, Any, List, Tuple

from app.agents import order_agent, billing_agent, product_agent, refund_agent, tech_support_agent
from app.services.database import db_service

logger = logging.getLogger(__name__)


def format_currency(val: Any) -> str:
    try:
        return f"{int(val):,}₫"
    except Exception:
        return str(val)


def fetch_domain_context(customer_id: str, message: str, intent: str, entities: Dict[str, Any]) -> Tuple[str, List[str]]:
    """
    Fetches real-world domain context based on user intent and extracted entities.
    Returns:
        (formatted_context_string, actions_taken_list)
    """
    actions_taken = []
    parts = []

    # 1. Tra cứu thông tin khách hàng nếu có
    customer = db_service.get_customer(customer_id)
    if customer:
        parts.append(f"Khách hàng: {customer.get('name')} (Hạng: {customer.get('loyalty_tier', 'Standard').upper()})")

    # 2. Xử lý theo Intent
    order_id = entities.get("order_id")

    if intent == "order_status":
        actions_taken.append("OrderAgent.check_order_status")
        if order_id:
            order_info = order_agent.check_order_status(customer_id, order_id)
            if "error" in order_info:
                parts.append(f"Không tìm thấy đơn hàng {order_id} của bạn.")
            else:
                items_str = ", ".join(f"{it.get('name')} (SL: {it.get('qty', 1)})" for it in order_info.get("items", []))
                status_vn = {
                    "processing": "Đang chuẩn bị hàng",
                    "shipped": "Đang giao hàng",
                    "delivered": "Giao thành công",
                    "cancelled": "Đã hủy",
                    "pending": "Chờ xác nhận",
                }.get(order_info.get("status"), order_info.get("status"))

                order_text = f"Đơn hàng: {order_info.get('order_id')}\n- Trạng thái: {status_vn}\n- Tổng tiền: {format_currency(order_info.get('total'))}\n- Sản phẩm: {items_str}"
                
                tracking = order_info.get("tracking")
                if tracking:
                    order_text += f"\n- Vận chuyển: {tracking.get('carrier')} (Mã vận đơn: {tracking.get('tracking_number')})\n- Tình trạng: {tracking.get('current_status')}\n- Dự kiến giao: {tracking.get('estimated_delivery')}"
                parts.append(order_text)
        else:
            # Lấy các đơn hàng gần đây của khách
            orders_data = order_agent.search_orders(customer_id)
            orders = orders_data.get("orders", [])
            if orders:
                recent = "\n".join(f"• {o.get('order_id')}: {format_currency(o.get('total'))} - Trạng thái: {o.get('status')}" for o in orders[:3])
                parts.append(f"Các đơn hàng gần nhất của bạn:\n{recent}")
            else:
                parts.append("Hiện chưa có đơn hàng nào được tạo.")

    elif intent in ("return_request", "refund"):
        actions_taken.append("OrderAgent.check_return_eligibility")
        actions_taken.append("RefundAgent.get_refund_status")
        if order_id:
            eligibility = order_agent.check_return_eligibility(customer_id, order_id)
            order_obj = db_service.get_order(order_id)
            if order_obj:
                items_str = ", ".join(f"{it.get('name')}" for it in order_obj.get("items", []))
                parts.append(
                    f"Thông tin đơn hàng {order_id}:\n"
                    f"- Trạng thái: {order_obj.get('status')}\n"
                    f"- Tổng giá trị: {format_currency(order_obj.get('total'))}\n"
                    f"- Sản phẩm: {items_str}\n"
                    f"- Đủ điều kiện đổi/trả: {'Có' if eligibility.get('eligible') else 'Không'}"
                )
            else:
                parts.append(f"Không tìm thấy đơn hàng {order_id}.")
        refund_status = refund_agent.get_refund_status(order_id=order_id)
        parts.append(f"Quy trình hoàn tiền: Trạng thái {refund_status.get('status')}, dự kiến xử lý trong 5-7 ngày làm việc.")

    elif intent == "billing":
        actions_taken.append("BillingAgent.check_payment")
        if order_id:
            payment = billing_agent.check_payment(customer_id, order_id)
            if "error" in payment:
                parts.append(f"Thông tin thanh toán đơn {order_id}: {payment['error']}")
            else:
                parts.append(
                    f"Thông tin thanh toán đơn {order_id}:\n"
                    f"- Mã thanh toán: {payment.get('payment_id')}\n"
                    f"- Số tiền: {format_currency(payment.get('amount'))}\n"
                    f"- Trạng thái: {'Đã thanh toán' if payment.get('status') == 'paid' else payment.get('status')}\n"
                    f"- Phương thức: {payment.get('method')}"
                )
        if entities.get("payment_issue") == "double_charge":
            parts.append("Lưu ý: Nếu bạn bị trừ tiền 2 lần, ngân hàng/ví sẽ tự động hoàn lại giao dịch trùng trong 3-5 ngày làm việc.")

    elif intent == "product_query":
        actions_taken.append("ProductAgent.search_products")
        query_text = entities.get("product_name") or message
        prod_res = product_agent.search_products(query=query_text)
        products = prod_res.get("products", [])
        if products:
            lines = []
            for p in products[:5]:
                orig = f" (Giá gốc: {format_currency(p['original_price'])})" if p.get("original_price") else ""
                lines.append(f"• {p.get('name')} ({p.get('product_id')}): {format_currency(p.get('price'))}{orig} - Đánh giá: {p.get('rating', 5.0)}/5")
            parts.append("Sản phẩm phù hợp tìm thấy:\n" + "\n".join(lines))
        else:
            parts.append("Không tìm thấy sản phẩm nào khớp với yêu cầu.")

    elif intent == "tech_support":
        actions_taken.append("TechSupportAgent.troubleshoot_issue")
        pname = entities.get("product_name", "may loc nuoc")
        symptom = entities.get("symptom", "")
        guide = tech_support_agent.troubleshoot_issue(customer_id, product_name=pname, symptom=symptom)
        steps = guide.get("troubleshooting_steps", [])
        if steps:
            steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
            parts.append(f"Hướng dẫn khắc phục sự cố ({pname} - {symptom}):\n{steps_text}")
        else:
            parts.append(f"Chưa có hướng dẫn tự xử lý cho triệu chứng: {symptom}. Vui lòng liên hệ kỹ thuật viên.")

    return "\n\n".join(parts), actions_taken
