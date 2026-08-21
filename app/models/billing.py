from tortoise.models import Model
from tortoise import fields
from enum import Enum


class PlanStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"


class Plan(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=80, unique=True)
    code = fields.CharField(max_length=40, unique=True)
    description = fields.TextField(null=True)
    monthly_price = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_users = fields.IntField(default=5)
    max_clients = fields.IntField(default=500)
    support_level = fields.CharField(max_length=40, default="standard")
    trial_days = fields.IntField(default=14)
    status = fields.CharEnumField(PlanStatus, default=PlanStatus.ACTIVE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "plans"
        indexes = [("code",), ("status",)]


class Subscription(Model):
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="subscriptions", on_delete=fields.CASCADE)
    plan = fields.ForeignKeyField("models.Plan", related_name="subscriptions", on_delete=fields.RESTRICT)
    status = fields.CharEnumField(SubscriptionStatus, default=SubscriptionStatus.TRIALING)
    started_at = fields.DatetimeField(auto_now_add=True)
    trial_ends_at = fields.DatetimeField(null=True)
    renews_at = fields.DatetimeField(null=True)
    canceled_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "subscriptions"
        indexes = [("tenant_id",), ("status",)]


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class Invoice(Model):
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="invoices", on_delete=fields.CASCADE)
    subscription = fields.ForeignKeyField("models.Subscription", related_name="invoices", null=True, on_delete=fields.SET_NULL)
    number = fields.CharField(max_length=40, unique=True)
    subtotal = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = fields.CharField(max_length=3, default="MXN")
    status = fields.CharEnumField(InvoiceStatus, default=InvoiceStatus.DRAFT)
    due_at = fields.DatetimeField(null=True)
    paid_at = fields.DatetimeField(null=True)
    provider = fields.CharField(max_length=40, null=True)
    provider_invoice_id = fields.CharField(max_length=120, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "invoices"
        indexes = [("tenant_id",), ("status",), ("created_at",)]
