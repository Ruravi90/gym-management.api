from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TenantCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    max_users: int = 10
    waha_session: Optional[str] = None
    waha_enabled: bool = False


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = None
    max_users: Optional[int] = None
    waha_session: Optional[str] = None
    waha_enabled: Optional[bool] = None


class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    status: str
    max_users: int
    created_at: datetime
    updated_at: datetime
    waha_session: Optional[str] = None
    waha_enabled: bool = False

    class Config:
        from_attributes = True


class TenantStats(BaseModel):
    tenant_id: int
    tenant_name: str
    total_users: int
    total_clients: int
    active_memberships: int
    total_revenue: float
