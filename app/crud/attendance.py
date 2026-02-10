from typing import List, Optional
from datetime import datetime, timezone
from app.models.attendance import Attendance
from app.models.client import Client
from tortoise.exceptions import DoesNotExist


async def get_attendance(attendance_id: int) -> Optional[Attendance]:
    """Get a specific attendance record by ID"""
    try:
        return await Attendance.get(id=attendance_id)
    except DoesNotExist:
        return None


async def get_attendance_records(skip: int = 0, limit: int = 100) -> List[Attendance]:
    """Get all attendance records with pagination"""
    return await Attendance.all().offset(skip).limit(limit)


async def get_attendance_by_client(client_id: int) -> List[Attendance]:
    """Get all attendance records for a specific client"""
    return await Attendance.filter(client_id=client_id)


async def get_attendance_today() -> List[Attendance]:
    """Get all attendance records for today"""
    today = datetime.now().date()
    return await Attendance.filter(
        check_in_time__date=today
    )


async def create_attendance(attendance_data: dict) -> Attendance:
    """Create a new attendance record"""
    return await Attendance.create(**attendance_data)


async def update_attendance(attendance_id: int, attendance_update: dict) -> Optional[Attendance]:
    """Update an attendance record"""
    attendance = await get_attendance(attendance_id)
    if attendance:
        for field, value in attendance_update.items():
            setattr(attendance, field, value)
        await attendance.save()
    return attendance


async def delete_attendance(attendance_id: int) -> Optional[Attendance]:
    """Delete an attendance record"""
    attendance = await get_attendance(attendance_id)
    if attendance:
        await attendance.delete()
    return attendance


async def check_in_client(client_id: int, device_id: str = None) -> Attendance:
    """Record a client's check-in"""
    attendance_data = {
        "client_id": client_id,
        "device_id": device_id
    }
    return await create_attendance(attendance_data)


async def check_out_client(attendance_id: int) -> Optional[Attendance]:
    """Record a client's check-out"""
    attendance = await get_attendance(attendance_id)
    if attendance:
        attendance.check_out_time = datetime.now(timezone.utc)
        await attendance.save()
    return attendance