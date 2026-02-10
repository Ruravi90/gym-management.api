from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class GymClassBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructor: str
    capacity: int
    start_time: datetime
    end_time: datetime
    status: str = "scheduled"  # scheduled, ongoing, completed, cancelled


class GymClassCreate(GymClassBase):
    pass


class GymClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    capacity: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class GymClass(GymClassBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
