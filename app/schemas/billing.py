from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str
    description: Optional[str] = None
    monthly_price: Decimal
    max_users: int
    max_clients: int
    support_level: str
    trial_days: int
    status: str


class PlanUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    monthly_price: Optional[Decimal] = None
    max_users: Optional[int] = None
    max_clients: Optional[int] = None
    support_level: Optional[str] = None
    trial_days: Optional[int] = None
    status: Optional[str] = None


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tenant_id: int
    plan_id: int
    status: str
    started_at: datetime
    trial_ends_at: Optional[datetime] = None
    renews_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    tenant_name: Optional[str] = None
    plan_name: Optional[str] = None


class SubscriptionAssignRequest(BaseModel):
    plan_id: int


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tenant_id: int
    subscription_id: Optional[int] = None
    number: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    currency: str
    status: str
    due_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    provider: Optional[str] = None
    provider_invoice_id: Optional[str] = None
    tenant_name: Optional[str] = None


class InvoiceCreateRequest(BaseModel):
    due_at: Optional[datetime] = None


class InvoiceStatusRequest(BaseModel):
    status: str
