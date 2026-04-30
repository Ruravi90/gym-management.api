from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from app.models.kaizen import KaizenLogStatus, MedalType


# Habit Schemas
class HabitBase(BaseModel):
    name: str
    reflection: Optional[str] = None
    goal: Optional[str] = None
    month: int
    year: int

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    reflection: Optional[str] = None
    goal: Optional[str] = None

class KaizenLogBase(BaseModel):
    date: date
    status: KaizenLogStatus
    reflection: Optional[str] = None

class KaizenLogCreate(KaizenLogBase):
    pass

class KaizenLogResponse(KaizenLogBase):
    id: int
    habit_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HabitResponse(HabitBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime
    logs: List[KaizenLogResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Medal Schemas
class MedalBase(BaseModel):
    type: MedalType
    description: str

class MedalResponse(MedalBase):
    id: int
    client_id: int
    earned_date: date

    model_config = ConfigDict(from_attributes=True)
