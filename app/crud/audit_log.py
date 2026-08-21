from typing import List, Optional
from datetime import datetime
from app.models.audit_log import AuditLog, ActionTypeEnum
from tortoise.exceptions import DoesNotExist

print("Loading audit_log CRUD module...")


async def create_audit_log(
    action_type: ActionTypeEnum,
    user_id: Optional[int],
    entity_type: str,
    entity_id: int,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> AuditLog:
    audit_log = await AuditLog.create(
        action_type=action_type,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        tenant_id=tenant_id,
    )
    return audit_log


async def get_audit_log(audit_log_id: int, tenant_id: Optional[int] = None) -> Optional[AuditLog]:
    try:
        filters = {"id": audit_log_id}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await AuditLog.get(**filters)
    except DoesNotExist:
        return None


async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    action_type: Optional[ActionTypeEnum] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    tenant_id: Optional[int] = None,
) -> List[AuditLog]:
    query = AuditLog.all()

    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    if user_id:
        query = query.filter(user_id=user_id)
    if entity_type:
        query = query.filter(entity_type=entity_type)
    if entity_id:
        query = query.filter(entity_id=entity_id)
    if action_type:
        query = query.filter(action_type=action_type)
    if start_date:
        query = query.filter(timestamp__gte=start_date)
    if end_date:
        query = query.filter(timestamp__lte=end_date)

    return await query.offset(skip).limit(limit).order_by("-timestamp")


async def get_audit_logs_by_entity(
    entity_type: str,
    entity_id: int,
    tenant_id: Optional[int] = None,
) -> List[AuditLog]:
    filters = {"entity_type": entity_type, "entity_id": entity_id}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await AuditLog.filter(**filters).order_by("-timestamp")


async def get_audit_logs_by_user(user_id: int, tenant_id: Optional[int] = None) -> List[AuditLog]:
    filters = {"user_id": user_id}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await AuditLog.filter(**filters).order_by("-timestamp")


async def get_audit_logs_by_action_type(action_type: ActionTypeEnum, tenant_id: Optional[int] = None) -> List[AuditLog]:
    filters = {"action_type": action_type}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await AuditLog.filter(**filters).order_by("-timestamp")
