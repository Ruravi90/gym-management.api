from tortoise.models import Model
from tortoise import fields


class MentorMessage(Model):
    """Mensajes del mentor IA guardados para historial del cliente."""
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="mentor_messages", on_delete=fields.CASCADE)
    role = fields.CharField(max_length=20)  # 'mentor' | 'system'
    content = fields.TextField()
    message_type = fields.CharField(max_length=30)  # 'checkin' | 'routine' | 'error' | 'welcome'
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "mentor_messages"
        indexes = [("client_id",), ("created_at",)]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
