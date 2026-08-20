from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime
from app.models.gamification import ActionType, CriteriaType


class XpLogResponse(BaseModel):
    id: int
    client_id: int
    action_type: ActionType
    xp_amount: int
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AchievementDefinitionResponse(BaseModel):
    id: int
    key: str
    name: str
    description: str
    icon: str
    xp_reward: int
    criteria_type: CriteriaType
    criteria_value: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ClientAchievementResponse(BaseModel):
    id: int
    client_id: int
    achievement_id: int
    earned_date: date
    achievement: AchievementDefinitionResponse

    model_config = ConfigDict(from_attributes=True)


class AchievementWithStatus(BaseModel):
    key: str
    name: str
    description: str
    icon: str
    xp_reward: int
    earned: bool
    earned_date: Optional[date] = None
    progress: int = 0
    target: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProgressSummary(BaseModel):
    level: int
    xp: int
    xp_for_next_level: int
    xp_progress_percent: float
    current_streak: int
    longest_streak: int


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None


class AwardResult(BaseModel):
    xp_gained: int
    new_xp_total: int
    old_level: int
    new_level: int
    leveled_up: bool
    description: str


class WeeklyChallengeResponse(BaseModel):
    id: int
    title: str
    description: str
    xp_reward: int
    criteria_type: CriteriaType
    criteria_value: int
    start_date: date
    end_date: date
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ClientChallengeResponse(BaseModel):
    id: int
    client_id: int
    challenge_id: int
    current_progress: int
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChallengeWithStatus(BaseModel):
    id: int
    title: str
    description: str
    xp_reward: int
    criteria_type: str
    criteria_value: int
    start_date: date
    end_date: date
    current_progress: int
    completed: bool
    completed_at: Optional[datetime] = None
    progress_percent: float = 0.0
