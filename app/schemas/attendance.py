from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AttendanceBase(BaseModel):
    client_id: int
    check_in: datetime
    check_out: Optional[datetime] = None
    date: datetime

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    check_out: Optional[datetime] = None

class Attendance(AttendanceBase):
    id: int

    class Config:
        from_attributes = True
