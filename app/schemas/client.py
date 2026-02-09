from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class ClientBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = "basic"

class ClientCreate(ClientBase):
    password: Optional[str] = None  # Optional initial password (clients usually don't need one)

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    membership_type: Optional[str] = None
    status: Optional[bool] = None
    profile_image: Optional[str] = None

class Client(ClientBase):
    id: int
    status: bool
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True