from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, date


class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = None  # basic, premium, vip
    status: bool = True
    birth_date: Optional[date] = None
    body_type: Optional[str] = None
    height_cm: Optional[float] = None
    sex: Optional[str] = None
    injuries: Optional[str] = None
    goal: Optional[str] = None
    restrictions: Optional[str] = None
    emergency_contact: Optional[str] = None

    @field_validator('email', 'phone', 'birth_date', 'sex', 'body_type', 'goal', 'injuries', 'restrictions', 'emergency_contact', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        return None if v == "" else v

    @field_validator('email', 'phone', 'birth_date', 'sex', 'body_type', 'goal', 'injuries', 'restrictions', 'emergency_contact', mode='before')
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
    birth_date: Optional[date] = None
    body_type: Optional[str] = None
    height_cm: Optional[float] = None
    sex: Optional[str] = None
    injuries: Optional[str] = None
    goal: Optional[str] = None
    restrictions: Optional[str] = None
    emergency_contact: Optional[str] = None
    birth_date: Optional[date] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    body_type: Optional[str] = None
    goal: Optional[str] = None
    injuries: Optional[str] = None
    restrictions: Optional[str] = None
    emergency_contact: Optional[str] = None


class Client(ClientBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
