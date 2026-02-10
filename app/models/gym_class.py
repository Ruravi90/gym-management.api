from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class GymClass(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    instructor = fields.CharField(max_length=100)
    capacity = fields.IntField()
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    status = fields.CharField(max_length=20, default="scheduled")  # scheduled, ongoing, completed, cancelled
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "classes"
        indexes = [("status",), ("start_time",), ("end_time",)]
    
    def __str__(self):
        return self.name