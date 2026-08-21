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
