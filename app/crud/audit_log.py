from typing import List, Optional
from datetime import datetime
from app.models.audit_log import AuditLog, ActionTypeEnum
from tortoise.exceptions import DoesNotExist

# Debug log to see if this file is being loaded
print("Loading audit_log CRUD module...")


async def create_audit_log(
    action_type: ActionTypeEnum,
    user_id: Optional[int],
    entity_type: str,
    entity_id: int,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Create a new audit log entry"""
    audit_log = await AuditLog.create(
        action_type=action_type,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent
    )
    return audit_log


async def get_audit_log(audit_log_id: int) -> Optional[AuditLog]:
    """Get a specific audit log entry by ID"""
    try:
        return await AuditLog.get(id=audit_log_id)
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
    end_date: Optional[datetime] = None
) -> List[AuditLog]:
    """Get audit logs with optional filters"""
    query = AuditLog.all()
    
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
    entity_id: int
) -> List[AuditLog]:
    """Get all audit logs for a specific entity"""
    return await AuditLog.filter(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by("-timestamp")


async def get_audit_logs_by_user(
    user_id: int
) -> List[AuditLog]:
    """Get all audit logs performed by a specific user"""
    return await AuditLog.filter(user_id=user_id).order_by("-timestamp")


async def get_audit_logs_by_action_type(
    action_type: ActionTypeEnum
) -> List[AuditLog]:
    """Get all audit logs of a specific action type"""
    return await AuditLog.filter(action_type=action_type).order_by("-timestamp")