import datetime
from app.database import SessionLocal, engine
from app.models import Base, User, Order
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(User).filter(User.email == "alice@example.com").first():
    alice = User(name="Alice Sharma", email="alice@example.com", password_hash=hash_password("Password123!"), role="customer")
    bob = User(name="Bob Verma", email="bob@example.com", password_hash=hash_password("Password123!"), role="customer")
    agent = User(name="Support Specialist", email="agent@example.com", password_hash=hash_password("Agent123!"), role="agent")
    db.add_all([alice, bob, agent])
    db.commit()
    db.refresh(alice)
    db.refresh(bob)

    now = datetime.datetime.utcnow()
    orders = [
        Order(id="ORD-1001", customer_id=alice.id, status="delivered", delivery_date=now - datetime.timedelta(days=2), total_amount=2499.0, item_name="Mechanical Keyboard", category="electronics"),
        Order(id="ORD-1002", customer_id=alice.id, status="delivered", delivery_date=now - datetime.timedelta(days=1), total_amount=14999.0, item_name="27-inch IPS Monitor", category="electronics"),
        Order(id="ORD-1003", customer_id=alice.id, status="delivered", delivery_date=now - datetime.timedelta(days=14), total_amount=999.0, item_name="Wireless Earbuds", category="electronics"),
        Order(id="ORD-2001", customer_id=bob.id, status="delivered", delivery_date=now - datetime.timedelta(days=1), total_amount=1800.0, item_name="Denim Jacket", category="fashion"),
    ]
    db.add_all(orders)
    db.commit()
    print("Database seeded successfully.")
db.close()