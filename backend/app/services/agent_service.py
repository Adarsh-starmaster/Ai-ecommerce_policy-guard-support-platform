import re
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Order, Ticket, Escalation
from app.services.refund_service import evaluate_and_process_refund, log_audit

POLICY_PATH = Path(__file__).resolve().parent.parent / "policies" / "return_policy.md"

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|system) instructions",
    r"override (policy|rules|limit)",
    r"approve regardless",
    r"you are now",
    r"system prompt",
]

def detect_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pat, lowered) for pat in INJECTION_PATTERNS)

def get_order_details(db: Session, customer_id: int, order_id: str) -> dict | None:
    order = db.query(Order).filter(Order.id == order_id, Order.customer_id == customer_id).first()
    if not order:
        return None
    return {
        "order_id": order.id,
        "status": order.status,
        "delivery_date": order.delivery_date.strftime("%Y-%m-%d") if order.delivery_date else None,
        "total_amount": order.total_amount,
        "item_name": order.item_name,
        "category": order.category,
    }

def search_return_policy(category: str) -> str:
    content = POLICY_PATH.read_text(encoding="utf-8")
    for line in content.splitlines():
        if category.lower() in line.lower():
            return line.strip()
    return "Standard 7-day return policy applies. Refunds above ₹5,000 require manual specialist review."

def escalate_to_human(db: Session, ticket_id: int, summary: str, priority: str = "high") -> int:
    esc = Escalation(ticket_id=ticket_id, summary=summary, priority=priority)
    db.add(esc)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        ticket.status = "escalated"
        ticket.priority = priority
    db.commit()
    db.refresh(esc)
    return esc.id

def run_support_agent(db: Session, customer_id: int, ticket: Ticket, user_message: str) -> str:
    if detect_prompt_injection(user_message):
        log_audit(db, customer_id, "PROMPT_INJECTION_BLOCKED", "ticket", str(ticket.id), user_message[:200])
        db.commit()
        return "I can only process requests within our standard store return and support policies. Please provide a valid Order ID."

    match = re.search(r"\bORD-\d+\b", user_message.upper())
    order_id = match.group(0) if match else ticket.order_id
    lower_msg = user_message.lower()

    if "policy" in lower_msg and "refund" not in lower_msg:
        cat = "electronics" if "electronic" in lower_msg else "fashion" if "fashion" in lower_msg else "home"
        return f"Return Policy: {search_return_policy(cat)}"

    if any(word in lower_msg for word in ["refund", "return", "money back"]):
        if not order_id:
            return "I'd be happy to help with your refund. Please provide your Order ID (for example, `ORD-1001`)."

        order_data = get_order_details(db, customer_id, order_id)
        if not order_data:
            return f"I couldn't find an order matching `{order_id}` under your account."

        policy_info = search_return_policy(order_data["category"])
        result = evaluate_and_process_refund(db, customer_id, ticket.id, order_id, order_data["total_amount"], user_message)

        if result["status"] == "approved":
            return f"Verified Order `{order_id}` ({policy_info}). Your refund of ₹{result['amount']} has been **approved** (Refund #{result['refund_id']})."
        elif result["status"] == "escalated":
            return f"Order `{order_id}` is ₹{order_data['total_amount']} (above ₹5,000). Your refund (#{result['refund_id']}) has been **escalated** to a support specialist."
        elif result["status"] in ("duplicate_prevented", "already_exists"):
            return f"A refund request (#{result['refund_id']}) already exists for Order `{order_id}` (Status: **{result['refund_status']}**)."
        else:
            return f"Refund rejected for Order `{order_id}`: {result['reason']}"

    if "order" in lower_msg or "status" in lower_msg or order_id:
        if not order_id:
            return "Please share your Order ID so I can check its status."
        order_data = get_order_details(db, customer_id, order_id)
        if not order_data:
            return f"Order `{order_id}` was not found in your account."
        return f"Order `{order_id}` (**{order_data['item_name']}**, ₹{order_data['total_amount']}) is **{order_data['status']}** (Delivered: {order_data['delivery_date'] or 'Pending'})."

    if "human" in lower_msg or "escalate" in lower_msg:
        esc_id = escalate_to_human(db, ticket.id, f"Customer requested agent: {user_message}", "medium")
        return f"Ticket escalated to human support (Escalation #{esc_id})."

    return "I can check order status, explain return policies, or process eligible refunds. How can I help?"