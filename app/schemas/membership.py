from typing import Optional, List, Union
from pydantic import BaseModel, field_validator
from datetime import datetime, date


class MembershipTypeBase(BaseModel):
    name: str
    duration_days: Optional[int] = None
    accesses_allowed: Optional[int] = None  # None means unlimited
    price: float
    description: Optional[str] = None
    is_active: bool = True


class MembershipTypeCreate(MembershipTypeBase):
    pass


class MembershipTypeUpdate(BaseModel):
    name: Optional[str] = None
    duration_days: Optional[int] = None
    accesses_allowed: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MembershipType(MembershipTypeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MembershipBase(BaseModel):
    client_id: int
    membership_type_id: Optional[int] = None  # New field referencing membership type
    type: Optional[str] = "basic"  # Kept for backward compatibility during migration
    start_date: Optional[Union[datetime, date]] = None
    end_date: Optional[Union[datetime, date]] = None
    price: Optional[float] = None
    price_paid: Optional[float] = None  # Actual price paid (may differ from type price)
    status: Optional[str] = "active"  # active, expired, suspended, cancelled
    payment_status: Optional[str] = "pending"  # pending, paid, overdue
    payment_method: Optional[str] = None  # cash, card, bank_transfer, online
    accesses_used: int = 0  # For punch-based memberships
    notes: Optional[str] = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_dates(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse as Date (YYYY-MM-DD)
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                pass
        return v


class MembershipCreate(MembershipBase):
    pass


class MembershipUpdate(BaseModel):
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


class PunchUsage(BaseModel):
    total_accesses_allowed: Optional[int]  # None means unlimited
    accesses_used: int
    accesses_remaining: Optional[int]  # None means unlimited

    class Config:
        from_attributes = True