from typing import List, Optional
from datetime import datetime, timedelta, timezone
from app.models.attendance import Attendance
from app.models.client import Client
from tortoise.exceptions import DoesNotExist
from app.services.audit_service import AuditService
from app.models.audit_log import ActionTypeEnum


async def get_attendance(attendance_id: int, tenant_id: Optional[int] = None) -> Optional[Attendance]:
    try:
        filters = {"id": attendance_id}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await Attendance.get(**filters)
    except DoesNotExist:
        return None


async def get_attendance_records(skip: int = 0, limit: int = 100, tenant_id: Optional[int] = None) -> List[Attendance]:
    query = Attendance.all()
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.offset(skip).limit(limit)


async def get_attendance_by_client(client_id: int, tenant_id: Optional[int] = None) -> List[Attendance]:
    filters = {"client_id": client_id}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Attendance.filter(**filters)


async def get_attendance_today(tenant_id: Optional[int] = None) -> List[Attendance]:
    today = datetime.now(timezone.utc).date()
    start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    start_of_tomorrow = start_of_today + timedelta(days=1)
    filters = {
        "check_in_time__gte": start_of_today,
        "check_in_time__lt": start_of_tomorrow,
    }
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Attendance.filter(**filters)


async def create_attendance(
    attendance_data: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Attendance:
    if tenant_id is not None:
        attendance_data["tenant_id"] = tenant_id
    attendance = await Attendance.create(**attendance_data)

    await AuditService.log_creation(
        user_id=user_id,
        entity_type="Attendance",
        entity_id=attendance.id,
        new_values=await AuditService.extract_entity_values_for_audit(attendance),
        ip_address=ip_address,
        user_agent=user_agent,
        tenant_id=tenant_id,
    )

    try:
        from app.services.gamification import GamificationService
        gamification = GamificationService()
        client_id = attendance_data.get("client_id")
        if client_id:
            await gamification.award_xp(client_id, "check_in", 10, "Check-in al gym", tenant_id=tenant_id)
            await gamification.update_streak(client_id)
    except Exception:
        pass

    return attendance


async def update_attendance(
    attendance_id: int,
    attendance_update: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[Attendance]:
    attendance = await get_attendance(attendance_id, tenant_id=tenant_id)
    if attendance:
        old_values = await AuditService.extract_entity_values_for_audit(attendance)

        for field, value in attendance_update.items():
            setattr(attendance, field, value)
        await attendance.save()

        new_values = await AuditService.extract_entity_values_for_audit(attendance)

        await AuditService.log_update(
            user_id=user_id,
            entity_type="Attendance",
            entity_id=attendance.id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )

    return attendance


async def delete_attendance(
    attendance_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[Attendance]:
    attendance = await get_attendance(attendance_id, tenant_id=tenant_id)
    if attendance:
        old_values = await AuditService.extract_entity_values_for_audit(attendance)

        await attendance.delete()

        await AuditService.log_deletion(
            user_id=user_id,
            entity_type="Attendance",
            entity_id=attendance.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )
    return attendance


async def check_in_client(client_id: int, device_id: str = None, tenant_id: Optional[int] = None) -> Attendance:
    attendance_data = {
        "client_id": client_id,
        "device_id": device_id
    }
    return await create_attendance(attendance_data, tenant_id=tenant_id)


async def check_out_client(attendance_id: int, tenant_id: Optional[int] = None) -> Optional[Attendance]:
    attendance = await get_attendance(attendance_id, tenant_id=tenant_id)
    if attendance:
        attendance.check_out_time = datetime.now(timezone.utc)
        await attendance.save()
    return attendance


async def update_attendance_checkout(attendance_id: int, check_out_time: datetime, tenant_id: Optional[int] = None) -> Optional[Attendance]:
    attendance = await get_attendance(attendance_id, tenant_id=tenant_id)
    if attendance:
        attendance.check_out_time = check_out_time
        await attendance.save()
    return attendance
