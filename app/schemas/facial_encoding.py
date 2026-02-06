from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class FacialEncodingBase(BaseModel):
    client_id: int

class FacialEncodingCreate(FacialEncodingBase):
    pass

class FacialEncodingUpdate(BaseModel):
    pass

class FacialEncoding(FacialEncodingBase):
    id: int
    client_id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True