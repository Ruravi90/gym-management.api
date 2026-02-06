from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class ClientBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = "basic"

class ClientCreate(ClientBase):
    password: str  # For client accounts if they need to log in

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
        orm_mode = True