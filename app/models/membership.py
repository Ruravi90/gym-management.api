from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class MembershipType(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)  # "Day Pass", "Weekly", "Monthly", "Annual"
    duration_days = fields.IntField(null=True)  # 1 for day pass, 7 for weekly, 30 for monthly, 365 for annual
    accesses_allowed = fields.IntField(null=True)  # None means unlimited, specific number for punch passes
    price = fields.FloatField()
    description = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relationship
    memberships: fields.ReverseRelation["Membership"]
    
    class Meta:
        table = "membership_types"
        indexes = [("is_active",), ("created_at",)]
    
    def __str__(self):
        return self.name


class Membership(Model):
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="memberships", on_delete=fields.CASCADE)
    membership_type = fields.ForeignKeyField(
        "models.MembershipType", related_name="memberships", null=True, on_delete=fields.SET_NULL
    )
    type = fields.CharField(max_length=50, default="basic")  # Kept for backward compatibility during migration
    start_date = fields.DatetimeField(auto_now_add=True)
    end_date = fields.DatetimeField()
    price = fields.FloatField()  # Original price
    price_paid = fields.FloatField(null=True)  # Actual price paid (may differ due to discounts)
    status = fields.CharField(max_length=20, default="active")  # active, expired, suspended, cancelled
    payment_status = fields.CharField(max_length=20, default="pending")  # pending, paid, overdue
    payment_method = fields.CharField(max_length=50, null=True)  # cash, card, bank_transfer, online
    accesses_used = fields.IntField(default=0)  # For punch-based memberships
    notes = fields.CharField(max_length=255, null=True)
    
    # Mercado Pago tracking
    mp_preference_id = fields.CharField(max_length=100, null=True)
    mp_payment_id = fields.CharField(max_length=100, null=True)
    mp_payment_status = fields.CharField(max_length=50, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "memberships"
        indexes = [("status",), ("payment_status",), ("start_date",), ("end_date",)]
    
    def __str__(self):
        return f"{self.client_id} - {self.type}"