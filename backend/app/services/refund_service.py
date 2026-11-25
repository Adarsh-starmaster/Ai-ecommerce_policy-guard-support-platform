import datetime
import hashlib
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Order, Refund, Escalation, Ticket, AuditLog
from app.config import AUTO_REFUND_LIMIT

RETURN_WINDOWS_DAYS = {"electronics": 7, "fashion": 15, "home": 10}

def log_audit(db: Session, actor_id: int | None, action: str, resource_type: str, resource_id: str, details: str = ""):
    db.add(AuditLog(actor_id=actor_id, action=action, resource_type=resource_type, resource_id=str(resource_id), details=details))

def evaluate_and_process_refund(
    db: Session, customer_id: int, ticket_id: int, order_id: str, amount: float, reason: str, idempotency_key: str | None = None
) -> dict:
    order = db.query(Order).filter(Order.id == order_id, Order.customer_id == customer_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or access denied.")

    key = idempotency_key or hashlib.sha256(f"{customer_id}:{order_id}:{ticket_id}".encode()).hexdigest()
    existing = db.query(Refund).filter(Refund.idempotency_key == key).first()
    if existing:
        return {"status": "duplicate_prevented", "refund_id": existing.id, "refund_status": existing.status}

    existing_order_refund = db.query(Refund).filter(Refund.order_id == order_id, Refund.status.in_(["pending", "approved"])).first()
    if existing_order_refund:
        return {"status": "already_exists", "refund_id": existing_order_refund.id, "refund_status": existing_order_refund.status}

    if order.status != "delivered" or not order.delivery_date:
        return {"status": "rejected", "reason": "Only delivered orders are eligible for a refund."}

    if amount <= 0 or amount > order.total_amount:
        return {"status": "rejected", "reason": f"Requested amount exceeds order total of ₹{order.total_amount}."}

    window_days = RETURN_WINDOWS_DAYS.get(order.category.lower(), 7)
    days_since_delivery = (datetime.datetime.utcnow() - order.delivery_date).days
    if days_since_delivery > window_days:
        log_audit(db, customer_id, "REFUND_REJECTED_WINDOW", "order", order_id, f"Delivered {days_since_delivery}d ago; max {window_days}d")
        db.commit()
        return {"status": "rejected", "reason": f"Return window expired ({window_days}-day limit; delivered {days_since_delivery} days ago)."}

    if amount > AUTO_REFUND_LIMIT:
        refund = Refund(order_id=order_id, ticket_id=ticket_id, amount=amount, reason=reason, status="pending", idempotency_key=key, requested_by=customer_id)
        db.add(refund)
        db.add(Escalation(ticket_id=ticket_id, summary=f"High-value refund ₹{amount} for {order_id}", priority="high"))
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.status = "escalated"
            ticket.priority = "high"
        log_audit(db, customer_id, "REFUND_ESCALATED", "order", order_id, f"₹{amount} exceeds ₹{int(AUTO_REFUND_LIMIT)}")
        db.commit()
        db.refresh(refund)
        return {"status": "escalated", "refund_id": refund.id, "reason": f"Refunds above ₹{int(AUTO_REFUND_LIMIT)} require human approval."}

    refund = Refund(order_id=order_id, ticket_id=ticket_id, amount=amount, reason=reason, status="approved", idempotency_key=key, requested_by=customer_id)
    db.add(refund)
    log_audit(db, customer_id, "REFUND_APPROVED", "order", order_id, f"Auto-approved ₹{amount}")
    db.commit()
    db.refresh(refund)
    return {"status": "approved", "refund_id": refund.id, "amount": amount, "reason": "Refund approved."}