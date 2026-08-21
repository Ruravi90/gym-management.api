from typing import Optional, Dict, Any
from app.models.audit_log import ActionTypeEnum
from app.crud import audit_log as audit_log_crud
from app.models.user import User

print("Loading audit_service...")


class AuditService:
    @staticmethod
    async def log_action(
        action_type: ActionTypeEnum,
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_id: Optional[int] = None,
    ):
        await audit_log_crud.create_audit_log(
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

    @staticmethod
    async def log_creation(
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        new_values: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_id: Optional[int] = None,
    ):
        await AuditService.log_action(
            action_type=ActionTypeEnum.CREATE,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )

    @staticmethod
    async def log_update(
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]],
        new_values: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_id: Optional[int] = None,
    ):
        await AuditService.log_action(
            action_type=ActionTypeEnum.UPDATE,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )

    @staticmethod
    async def log_deletion(
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_id: Optional[int] = None,
    ):
        await AuditService.log_action(
            action_type=ActionTypeEnum.DELETE,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )

    @staticmethod
    async def extract_entity_values_for_audit(entity) -> Dict[str, Any]:
        values = {}
        for field_name in entity._meta.db_fields:
            if field_name != 'id':
                try:
                    value = getattr(entity, field_name)
                    if hasattr(value, '_pk'):
                        values[field_name] = value._pk
                    elif hasattr(value, 'isoformat'):
                        values[field_name] = value.isoformat() if value else None
                    elif isinstance(value, bytes):
                        values[field_name] = str(value, 'utf-8', errors='ignore') if value else None
                    elif hasattr(value, '__dict__'):
                        values[field_name] = str(value)
                    else:
                        values[field_name] = value
                except AttributeError:
                    continue
                except Exception:
                    values[field_name] = str(getattr(entity, field_name, None))
        return values
