from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from ..models.user_role import UserRole

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = UserRole.MEMBER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    status: Optional[bool] = None

class User(UserBase):
    id: int
    status: bool
    created_at: datetime

    class Config:
        from_attributes = True
