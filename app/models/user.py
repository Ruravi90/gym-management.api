from tortoise.models import Model
from tortoise import fields
from enum import Enum
from datetime import datetime


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    RECEPTIONIST = "receptionist"
    USER = "user"
    SUPER_ADMIN = "super_admin"


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, unique=True, null=True)
    phone = fields.CharField(max_length=20, null=True)
    role = fields.CharEnumField(UserRoleEnum, default=UserRoleEnum.USER)
    hashed_password = fields.CharField(max_length=100)
    status = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "users"
        indexes = [("email",), ("role",), ("created_at",)]
    
    def __str__(self):
        return self.name