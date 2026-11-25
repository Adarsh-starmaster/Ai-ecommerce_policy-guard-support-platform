from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Refund, Escalation, Ticket, User
from app.schemas import RefundDecisionRequest
from app.auth import get_current_user, require_agent
from app.services.refund_service import log_audit

router = APIRouter(prefix="/api/refunds", tags=["Refunds"])

@router.get("")
def list_refunds(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "agent":
        return db.query(Refund).order_by(Refund.created_at.desc()).all()
    return db.query(Refund).filter(Refund.requested_by == user.id).order_by(Refund.created_at.desc()).all()

@router.post("/{refund_id}/review")
def review_refund(refund_id: int, req: RefundDecisionRequest, agent: User = Depends(require_agent), db: Session = Depends(get_db)):
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")
    if req.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Decision must be approved or rejected")

    refund.status = req.decision
    refund.reviewed_by = agent.id

    esc = db.query(Escalation).filter(Escalation.ticket_id == refund.ticket_id).first()
    if esc:
        esc.decision = req.decision
        esc.assigned_to = agent.id
        esc.internal_note = req.internal_note

    ticket = db.query(Ticket).filter(Ticket.id == refund.ticket_id).first()
    if ticket:
        ticket.status = "resolved"

    log_audit(db, agent.id, f"REFUND_{req.decision.upper()}_BY_AGENT", "refund", str(refund.id), req.internal_note or "")
    db.commit()
    return refund