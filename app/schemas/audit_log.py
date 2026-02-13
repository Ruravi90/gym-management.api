from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# Debug log to see if this file is being loaded
print("Loading audit_log schema...")

class ActionTypeEnum(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLogBase(BaseModel):
    action_type: ActionTypeEnum
    user_id: Optional[int] = None
    entity_type: str
    entity_id: int
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(BaseModel):
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None


class AuditLog(AuditLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True