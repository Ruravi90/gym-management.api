from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str = "user"  # admin, manager, receptionist, user, super_admin

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


class User(UserBase):
    id: int
    status: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True