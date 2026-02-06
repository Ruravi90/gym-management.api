from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class MembershipBase(BaseModel):
    client_id: int
    type: str  # basic, premium, vip
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    price: float
    status: Optional[str] = "active"  # active, expired, suspended, cancelled
    payment_status: Optional[str] = "pending"  # pending, paid, overdue
    payment_method: Optional[str] = None  # cash, card, bank_transfer, online
    notes: Optional[str] = None

class MembershipCreate(MembershipBase):
    pass

class MembershipUpdate(BaseModel):
    type: Optional[str] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class Membership(MembershipBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MembershipStatistics(BaseModel):
    total_memberships: int
    active_memberships: int
    expired_memberships: int
    upcoming_expirations: int
    upcoming_expirations_list: List[Membership]

    class Config:
        from_attributes = True
