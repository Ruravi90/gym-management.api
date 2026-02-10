from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    membership_type: Optional[str] = None  # basic, premium, vip
    status: bool = True


class ClientCreate(ClientBase):
    password: Optional[str] = None  # Optional initial password (clients usually don't need one)


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = None
    status: Optional[bool] = None


class Client(ClientBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True