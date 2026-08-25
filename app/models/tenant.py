from tortoise.models import Model
from tortoise import fields
from enum import Enum


class TenantStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Tenant(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=150)
    slug = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, null=True)
    phone = fields.CharField(max_length=20, null=True)
    address = fields.TextField(null=True)
    logo_url = fields.CharField(max_length=500, null=True)
    status = fields.CharEnumField(TenantStatus, default=TenantStatus.ACTIVE)
    max_users = fields.IntField(default=10)
    waha_session = fields.CharField(max_length=100, null=True)
    waha_enabled = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tenants"
        indexes = [("slug",), ("status",), ("created_at",)]

    def __str__(self):
        return self.name
