from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import auth_router, orders_router, tickets_router, refunds_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce AI Customer Support API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(orders_router.router)
app.include_router(tickets_router.router)
app.include_router(refunds_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}