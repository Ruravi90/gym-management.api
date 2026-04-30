from tortoise.models import Model
from tortoise import fields
from enum import Enum


class KaizenLogStatus(str, Enum):
    PENDING = "pending"
    VICTORY = "victory"
    DEFEAT = "defeat"


class MedalType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class KaizenHabit(Model):
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="kaizen_habits", on_delete=fields.CASCADE)
    name = fields.CharField(max_length=255)
    reflection = fields.TextField(null=True)
    goal = fields.TextField(null=True)
    month = fields.IntField()  # 1-12
    year = fields.IntField()   # e.g., 2026
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "kaizen_habits"
        indexes = [("client_id", "month", "year")]

    def __str__(self):
        return f"{self.name} - {self.month}/{self.year}"


class KaizenLog(Model):
    id = fields.IntField(pk=True)
    habit = fields.ForeignKeyField("models.KaizenHabit", related_name="logs", on_delete=fields.CASCADE)
    date = fields.DateField()
    status = fields.CharEnumField(KaizenLogStatus, default=KaizenLogStatus.PENDING)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "kaizen_logs"
        unique_together = (("habit_id", "date"),)
        indexes = [("habit_id", "date")]

    def __str__(self):
        return f"{self.habit.name} - {self.date} - {self.status}"


class KaizenMedal(Model):
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="kaizen_medals", on_delete=fields.CASCADE)
    type = fields.CharEnumField(MedalType)
    description = fields.CharField(max_length=255)
    earned_date = fields.DateField(auto_now_add=True)

    class Meta:
        table = "kaizen_medals"
        indexes = [("client_id", "type")]

    def __str__(self):
        return f"{self.type} medal for {self.client_id}"
