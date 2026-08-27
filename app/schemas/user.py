from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str = "user"  # admin, manager, receptionist, user, super_admin

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        if v in (None, ''):
            return None
        value = str(v).strip()
        if not value.isdigit() or len(value) != 10:
            raise ValueError('El teléfono debe contener exactamente 10 dígitos numéricos')
        return value

    @field_validator('email', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    status: Optional[bool] = None

    @field_validator('email', mode='before')
    @classmethod
    def normalize_email(cls, v):
        if v in (None, ''):
            return None
        return str(v).strip().lower()


class User(UserBase):
    id: int
    status: bool = True
    tenant_id: Optional[int] = None
    tenant_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
