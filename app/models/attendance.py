from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class Attendance(Model):
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="attendances", on_delete=fields.CASCADE)
    check_in_time = fields.DatetimeField(auto_now_add=True)
    check_out_time = fields.DatetimeField(null=True)
    device_id = fields.CharField(max_length=100, null=True)  # For facial recognition device
    notes = fields.CharField(max_length=255, null=True)
    
    class Meta:
        table = "attendance"
        indexes = [("check_in_time",), ("check_out_time",)]
    
    def __str__(self):
        return f"Attendance {self.id} - Client {self.client_id}"