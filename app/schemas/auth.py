from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None

class UserRegister(UserLogin):
    name: str
    phone: Optional[str] = None

