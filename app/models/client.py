from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class Client(Model):
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="clients", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, null=True)
    phone = fields.CharField(max_length=20, null=True)
    # Identidad y perfil propios del socio; no dependen de User.
    hashed_password = fields.CharField(max_length=100, null=True)
    password_reset_token_hash = fields.CharField(max_length=128, null=True)
    password_reset_expires_at = fields.DatetimeField(null=True)
    birth_date = fields.DateField(null=True)
    body_type = fields.CharField(max_length=20, null=True)
    height_cm = fields.FloatField(null=True)
    age = fields.IntField(null=True)
    sex = fields.CharField(max_length=10, null=True)
    daily_activity = fields.CharField(max_length=20, null=True)
    injuries = fields.TextField(null=True)
    goal = fields.CharField(max_length=30, null=True)
    restrictions = fields.TextField(null=True)
    emergency_contact = fields.CharField(max_length=150, null=True)
    membership_type = fields.CharField(max_length=50, null=True)  # basic, premium, vip
    status = fields.BooleanField(default=True)
    last_weekly_checkin_at = fields.DatetimeField(null=True)
    last_monthly_report_at = fields.DatetimeField(null=True)

    # Gamification fields
    xp = fields.IntField(default=0)
    level = fields.IntField(default=1)
    current_streak = fields.IntField(default=0)
    longest_streak = fields.IntField(default=0)
    last_activity_date = fields.DateField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "clients"
        indexes = [("email",), ("status",), ("created_at",), ("membership_type",)]
    
    def __str__(self):
        return self.name
