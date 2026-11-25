from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ticket, Message, Escalation, Refund, User
from app.schemas import TicketCreateRequest, MessageCreateRequest, TicketUpdateRequest
from app.auth import get_current_user, require_agent
from app.services.agent_service import run_support_agent

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.get("")
def list_tickets(status: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Ticket)
    if user.role != "agent":
        q = q.filter(Ticket.customer_id == user.id)
    if status:
        q = q.filter(Ticket.status == status)
    return q.order_by(Ticket.created_at.desc()).all()


@router.post("")
def create_ticket(req: TicketCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = Ticket(
        customer_id=user.id,
        order_id=req.order_id or None,
        subject=req.subject,
        description=req.description,
        category=req.category,
        priority=req.priority,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    user_msg = Message(ticket_id=ticket.id, sender_type="customer", content=req.description)
    db.add(user_msg)
    reply_text = run_support_agent(db, user.id, ticket, req.description)
    agent_msg = Message(ticket_id=ticket.id, sender_type="ai_agent", content=reply_text)
    db.add(agent_msg)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}")
def get_ticket_detail(ticket_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket or (user.role != "agent" and ticket.customer_id != user.id):
        raise HTTPException(status_code=404, detail="Ticket not found")
    messages = db.query(Message).filter(Message.ticket_id == ticket_id).order_by(Message.created_at.asc()).all()
    escalations = db.query(Escalation).filter(Escalation.ticket_id == ticket_id).all()
    refunds = db.query(Refund).filter(Refund.ticket_id == ticket_id).all()
    return {"ticket": ticket, "messages": messages, "escalations": escalations, "refunds": refunds}


@router.post("/{ticket_id}/messages")
def post_message(ticket_id: int, req: MessageCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket or (user.role != "agent" and ticket.customer_id != user.id):
        raise HTTPException(status_code=404, detail="Ticket not found")

    sender = "support_agent" if user.role == "agent" else "customer"
    msg = Message(ticket_id=ticket_id, sender_type=sender, content=req.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    agent_reply = None
    if user.role == "customer":
        reply_text = run_support_agent(db, user.id, ticket, req.content)
        agent_reply = Message(ticket_id=ticket_id, sender_type="ai_agent", content=reply_text)
        db.add(agent_reply)
        db.commit()
        db.refresh(agent_reply)

    return {"message": msg, "agent_reply": agent_reply}


@router.patch("/{ticket_id}")
def update_ticket(ticket_id: int, req: TicketUpdateRequest, agent: User = Depends(require_agent), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = req.status
    if req.internal_note:
        db.add(Escalation(ticket_id=ticket_id, summary="Agent Note", priority=ticket.priority, assigned_to=agent.id, internal_note=req.internal_note))
    db.commit()
    db.refresh(ticket)
    return ticket