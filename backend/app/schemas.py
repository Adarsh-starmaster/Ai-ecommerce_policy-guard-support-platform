from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = "customer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TicketCreateRequest(BaseModel):
    subject: str = Field(..., min_length=3)
    description: str = Field(..., min_length=3)
    category: str
    order_id: Optional[str] = None
    priority: str = "medium"

class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)

class RefundDecisionRequest(BaseModel):
    decision: str # approved | rejected
    internal_note: Optional[str] = ""

class TicketUpdateRequest(BaseModel):
    status: str # open | escalated | resolved | closed
    internal_note: Optional[str] = None