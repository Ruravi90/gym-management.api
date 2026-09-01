from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class Client(Model):
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="clients", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, null=True)
    phone = fields.CharField(max_length=20, null=True)
    membership_type = fields.CharField(max_length=50, null=True)  # basic, premium, vip
    status = fields.BooleanField(default=True)
    user = fields.ForeignKeyField("models.User", related_name="client_profile", null=True, on_delete=fields.SET_NULL)
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

    @property
    def birth_date(self): return self.user.birth_date if self.user else None
    @property
    def body_type(self): return self.user.body_type if self.user else None
    @property
    def height_cm(self): return self.user.height_cm if self.user else None
    @property
    def sex(self): return self.user.sex if self.user else None
    @property
    def injuries(self): return self.user.injuries if self.user else None
    @property
    def goal(self): return self.user.goal if self.user else None
    @property
    def restrictions(self): return self.user.restrictions if self.user else None
    @property
    def emergency_contact(self): return self.user.emergency_contact if self.user else None
