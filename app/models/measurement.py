from tortoise.models import Model
from tortoise import fields


class BodyMeasurement(Model):
    """Medidas corporales del cliente (registro semanal). Todas las medidas en cm."""
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="body_measurements", null=True, on_delete=fields.SET_NULL)
    client = fields.ForeignKeyField("models.Client", related_name="body_measurements", on_delete=fields.CASCADE)
    date = fields.DateField()
    weight_kg = fields.DecimalField(max_digits=6, decimal_places=2, null=True)
    waist_cm = fields.DecimalField(max_digits=6, decimal_places=2, null=True)        # cintura
    abdomen_low_cm = fields.DecimalField(max_digits=6, decimal_places=2, null=True)  # abdomen bajo
    thigh_cm = fields.DecimalField(max_digits=6, decimal_places=2, null=True)        # pierna
    arm_relaxed_cm = fields.DecimalField(max_digits=6, decimal_places=2, null=True)  # brazo sin fuerza
    arm_flexed_cm = fields.DecimalField(max_digits=6, decimal_places=2, null=True)   # brazo con fuerza
    notes = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "body_measurements"
        unique_together = (("client_id", "date"),)
        indexes = [("client_id", "date")]

    def __str__(self):
        return f"Medidas {self.date} - cliente {self.client_id}"
