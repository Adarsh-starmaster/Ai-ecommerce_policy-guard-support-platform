from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("")
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "agent":
        return db.query(Order).all()
    return db.query(Order).filter(Order.customer_id == user.id).all()

@router.get("/{order_id}")
def get_order(order_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or (user.role != "agent" and order.customer_id != user.id):
        raise HTTPException(status_code=404, detail="Order not found")
    return order