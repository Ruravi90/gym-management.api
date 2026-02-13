from tortoise.models import Model
from tortoise import fields
from datetime import datetime
from enum import Enum

# Debug log to see if this file is being loaded
print("Loading audit_log model...")

class ActionTypeEnum(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLog(Model):
    id = fields.IntField(pk=True)
    action_type = fields.CharEnumField(ActionTypeEnum, max_length=10)
    user_id = fields.IntField(null=True)  # ID of the user who performed the action
    entity_type = fields.CharField(max_length=50)  # Type of entity (Client, Membership, etc.)
    entity_id = fields.IntField()  # ID of the entity that was affected
    old_values = fields.JSONField(null=True)  # Previous values before the change
    new_values = fields.JSONField(null=True)  # New values after the change
    timestamp = fields.DatetimeField(auto_now_add=True)
    ip_address = fields.CharField(max_length=45, null=True)  # Support for IPv6
    user_agent = fields.CharField(max_length=500, null=True)  # Browser/device info

    class Meta:
        table = "audit_logs"
        indexes = [
            ("timestamp",), 
            ("entity_type", "entity_id"),
            ("user_id",),
            ("action_type",)
        ]

    def __str__(self):
        return f"AuditLog {self.id} - {self.action_type} {self.entity_type}:{self.entity_id}"