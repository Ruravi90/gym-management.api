from tortoise.models import Model
from tortoise import fields
from enum import Enum


class ActionType(str, Enum):
    CHECK_IN = "check_in"
    KAIZEN_VICTORY = "kaizen_victory"
    WORKOUT_COMPLETED = "workout_completed"
    SET_LOGGED = "set_logged"
    MEASUREMENT_LOGGED = "measurement_logged"
    STREAK_BONUS = "streak_bonus"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"


class CriteriaType(str, Enum):
    CHECKINS_TOTAL = "checkins_total"
    STREAK_DAYS = "streak_days"
    KAIZEN_VICTORIES = "kaizen_victories"
    WORKOUTS_COMPLETED = "workouts_completed"
    SETS_TOTAL = "sets_total"
    MEASUREMENTS_TOTAL = "measurements_total"
    XP_TOTAL = "xp_total"
    LEVEL_REACHED = "level_reached"


class XpLog(Model):
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="xp_logs", on_delete=fields.CASCADE)
    action_type = fields.CharEnumField(ActionType)
    xp_amount = fields.IntField()
    description = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "xp_logs"
        indexes = [("client_id", "created_at"), ("client_id", "action_type")]

    def __str__(self):
        return f"{self.action_type}: +{self.xp_amount} XP for client {self.client_id}"


class AchievementDefinition(Model):
    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=50, unique=True)
    name = fields.CharField(max_length=100)
    description = fields.CharField(max_length=255)
    icon = fields.CharField(max_length=10, default="🏆")
    xp_reward = fields.IntField(default=0)
    criteria_type = fields.CharEnumField(CriteriaType)
    criteria_value = fields.IntField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "achievement_definitions"

    def __str__(self):
        return f"{self.name} ({self.key})"


class ClientAchievement(Model):
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="achievements", on_delete=fields.CASCADE)
    achievement = fields.ForeignKeyField("models.AchievementDefinition", related_name="earned_by", on_delete=fields.CASCADE)
    earned_date = fields.DateField(auto_now_add=True)

    class Meta:
        table = "client_achievements"
        unique_together = (("client_id", "achievement_id"),)

    def __str__(self):
        return f"Achievement {self.achievement_id} for client {self.client_id}"


class WeeklyChallenge(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100)
    description = fields.CharField(max_length=255)
    xp_reward = fields.IntField(default=0)
    criteria_type = fields.CharEnumField(CriteriaType)
    criteria_value = fields.IntField()
    start_date = fields.DateField()
    end_date = fields.DateField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "weekly_challenges"
        indexes = [("start_date", "end_date"), ("is_active",)]

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"


class ClientChallenge(Model):
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField("models.Client", related_name="challenges", on_delete=fields.CASCADE)
    challenge = fields.ForeignKeyField("models.WeeklyChallenge", related_name="participants", on_delete=fields.CASCADE)
    current_progress = fields.IntField(default=0)
    completed = fields.BooleanField(default=False)
    completed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "client_challenges"
        unique_together = (("client_id", "challenge_id"),)

    def __str__(self):
        return f"Challenge {self.challenge_id} for client {self.client_id}: {self.current_progress}"
