from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class AttendanceBase(BaseModel):
    client_id: int
    device_id: Optional[str] = None  # For facial recognition device
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    check_out_time: Optional[datetime] = None
    notes: Optional[str] = None


class Attendance(AttendanceBase):
    id: int
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True