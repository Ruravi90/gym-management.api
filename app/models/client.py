from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class Client(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, unique=True)
    phone = fields.CharField(max_length=20, null=True)
    membership_type = fields.CharField(max_length=50, null=True)  # basic, premium, vip
    status = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "clients"
        indexes = [("email",), ("status",), ("created_at",), ("membership_type",)]
    
    def __str__(self):
        return self.name