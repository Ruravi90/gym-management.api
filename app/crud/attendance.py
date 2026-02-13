from typing import List, Optional
from datetime import datetime, timezone
from app.models.attendance import Attendance
from app.models.client import Client
from tortoise.exceptions import DoesNotExist
from app.services.audit_service import AuditService
from app.models.audit_log import ActionTypeEnum


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


async def create_attendance(
    attendance_data: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Attendance:
    """Create a new attendance record"""
    attendance = await Attendance.create(**attendance_data)

    # Log the creation in the audit log
    await AuditService.log_creation(
        user_id=user_id,
        entity_type="Attendance",
        entity_id=attendance.id,
        new_values=await AuditService.extract_entity_values_for_audit(attendance),
        ip_address=ip_address,
        user_agent=user_agent
    )

    return attendance


async def update_attendance(
    attendance_id: int,
    attendance_update: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[Attendance]:
    """Update an attendance record"""
    attendance = await get_attendance(attendance_id)
    if attendance:
        # Get the old values before updating
        old_values = await AuditService.extract_entity_values_for_audit(attendance)

        # Update the attendance
        for field, value in attendance_update.items():
            setattr(attendance, field, value)
        await attendance.save()

        # Get the new values after updating
        new_values = await AuditService.extract_entity_values_for_audit(attendance)

        # Log the update in the audit log
        await AuditService.log_update(
            user_id=user_id,
            entity_type="Attendance",
            entity_id=attendance.id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    return attendance


async def delete_attendance(
    attendance_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[Attendance]:
    """Delete an attendance record"""
    attendance = await get_attendance(attendance_id)
    if attendance:
        # Get the old values before deleting
        old_values = await AuditService.extract_entity_values_for_audit(attendance)

        await attendance.delete()

        # Log the deletion in the audit log
        await AuditService.log_deletion(
            user_id=user_id,
            entity_type="Attendance",
            entity_id=attendance.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
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


async def update_attendance_checkout(attendance_id: int, check_out_time: datetime) -> Optional[Attendance]:
    """Update an attendance record with check-out time"""
    attendance = await get_attendance(attendance_id)
    if attendance:
        attendance.check_out_time = check_out_time
        await attendance.save()
    return attendance