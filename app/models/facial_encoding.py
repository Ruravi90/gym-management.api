from tortoise.models import Model
from tortoise import fields
from datetime import datetime
from .client import Client


class FacialEncoding(Model):
    id = fields.IntField(pk=True)
    client_id = fields.IntField()  # Foreign key reference
    encoding_data = fields.TextField()  # Store the facial encoding as text
    image_path = fields.CharField(max_length=255, null=True)  # Path to the reference image
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relationship
    client: fields.ReverseRelation["Client"]
    
    class Meta:
        table = "facial_encodings"
        indexes = [("client_id",), ("created_at",)]
    
    def __str__(self):
        return f"Facial Encoding {self.id} - Client {self.client_id}"