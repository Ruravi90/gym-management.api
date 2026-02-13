from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = None  # basic, premium, vip
    status: bool = True

    @field_validator('email', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


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