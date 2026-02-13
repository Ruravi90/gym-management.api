from typing import Optional, Dict, Any
from app.models.audit_log import ActionTypeEnum
from app.crud import audit_log as audit_log_crud
from app.models.user import User

# Debug log to see if this file is being loaded
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
        user_agent: Optional[str] = None
    ):
        """
        Generic method to log an action in the audit log
        """
        await audit_log_crud.create_audit_log(
            action_type=action_type,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    async def log_creation(
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        new_values: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log a creation action
        """
        await AuditService.log_action(
            action_type=ActionTypeEnum.CREATE,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    async def log_update(
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]],
        new_values: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log an update action
        """
        await AuditService.log_action(
            action_type=ActionTypeEnum.UPDATE,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    async def log_deletion(
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log a deletion action
        """
        await AuditService.log_action(
            action_type=ActionTypeEnum.DELETE,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    async def extract_entity_values_for_audit(entity) -> Dict[str, Any]:
        """
        Extract values from an entity for audit logging
        This method converts a Tortoise ORM model instance to a dictionary
        """
        # Convert the model instance to a dictionary
        # Exclude the 'id' field as it's already stored separately in the audit log
        values = {}

        # Get the model's fields - only use actual database fields to avoid QuerySets from relationships
        for field_name in entity._meta.db_fields:
            if field_name != 'id':
                try:
                    value = getattr(entity, field_name)

                    # Handle special cases for different field types
                    if hasattr(value, '_pk'):  # Foreign key reference
                        values[field_name] = value._pk
                    elif hasattr(value, 'isoformat'):  # Datetime objects
                        values[field_name] = value.isoformat() if value else None
                    elif isinstance(value, bytes):  # Binary data
                        values[field_name] = str(value, 'utf-8', errors='ignore') if value else None
                    elif hasattr(value, '__dict__'):  # Nested objects
                        # For nested objects, try to convert to dict or string representation
                        values[field_name] = str(value)
                    else:
                        values[field_name] = value
                except AttributeError:
                    # If the attribute doesn't exist, skip it
                    continue
                except Exception:
                    # For any other error, store a string representation
                    values[field_name] = str(getattr(entity, field_name, None))

        return values