from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date, datetime


# ---------------------------------------------------------------
# Exercise
# ---------------------------------------------------------------
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_group: Optional[str] = None
    body_part: Optional[str] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = "beginner"
    target: Optional[str] = None
    secondary_muscles: Optional[str] = None
    instructions: Optional[str] = None
    gif_url: Optional[str] = None
    image_url: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    muscle_group: Optional[str] = None
    body_part: Optional[str] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    target: Optional[str] = None
    secondary_muscles: Optional[str] = None
    instructions: Optional[str] = None
    gif_url: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ExerciseResponse(ExerciseBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# Routine
# ---------------------------------------------------------------
class RoutineExerciseBase(BaseModel):
    exercise_id: int
    sets: int = 3
    reps: str = "10"
    weight: Optional[str] = None
    rest_seconds: int = 60
    notes: Optional[str] = None
    order: int = 0


class RoutineExerciseCreate(RoutineExerciseBase):
    pass


class RoutineExerciseResponse(RoutineExerciseBase):
    id: int
    day_id: int
    exercise: Optional[ExerciseResponse] = None

    model_config = ConfigDict(from_attributes=True)


class RoutineDayBase(BaseModel):
    name: str
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    order: int = 0


class RoutineDayCreate(RoutineDayBase):
    exercises: List[RoutineExerciseCreate] = []


class RoutineDayResponse(RoutineDayBase):
    id: int
    routine_id: int
    exercises: List[RoutineExerciseResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RoutineBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class RoutineCreate(RoutineBase):
    # Si no se envía, la rutina se asigna al cliente autenticado
    client_id: Optional[int] = None
    days: List[RoutineDayCreate] = []


class RoutineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    # Si se envía, reemplaza por completo los días de la rutina
    days: Optional[List[RoutineDayCreate]] = None


class RoutineResponse(RoutineBase):
    id: int
    client_id: int
    # En Tortoise el FK se expone como <campo>_id; leemos ese atributo sin cambiar la clave JSON
    created_by: Optional[int] = Field(default=None, validation_alias="created_by_id")
    created_at: datetime
    updated_at: datetime
    days: List[RoutineDayResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# Workout sessions (seguimiento)
# ---------------------------------------------------------------
class WorkoutSessionCreate(BaseModel):
    routine_id: Optional[int] = None
    day_id: Optional[int] = None
    notes: Optional[str] = None


class WorkoutSessionUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None
    duration_minutes: Optional[int] = None


class SetLogCreate(BaseModel):
    exercise_id: int
    set_number: int = Field(ge=1)
    reps: Optional[int] = Field(default=None, ge=0)
    weight: Optional[str] = None
    completed: bool = True


class SetLogUpdate(BaseModel):
    reps: Optional[int] = Field(default=None, ge=0)
    weight: Optional[str] = None
    completed: Optional[bool] = None


class SetLogResponse(BaseModel):
    id: int
    session_id: int
    exercise_id: int
    exercise: Optional[ExerciseResponse] = None
    set_number: int
    reps: Optional[int] = None
    weight: Optional[str] = None
    completed: bool

    model_config = ConfigDict(from_attributes=True)


class WorkoutSessionResponse(BaseModel):
    id: int
    client_id: int
    routine_id: Optional[int] = None
    day_id: Optional[int] = None
    date: date
    notes: Optional[str] = None
    status: str
    duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    set_logs: List[SetLogResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------
# Mentor IA
# ---------------------------------------------------------------
class MentorRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class MentorResponse(BaseModel):
    reply: str
    provider: Optional[str] = None


class MentorMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    message_type: str
    created_at: datetime

    class Config:
        from_attributes = True


BODY_TYPES = {"ectomorph", "mesomorph", "endomorph"}


class BodyTypeRequest(BaseModel):
    body_type: str = Field(min_length=1, max_length=20)


class BodyTypeResponse(BaseModel):
    body_type: Optional[str] = None
    reply: str


class ProfileUpdate(BaseModel):
    """Datos del perfil físico que un instructor pregunta antes de asignar una rutina."""
    body_type: Optional[str] = None
    height_cm: Optional[float] = Field(default=None, ge=80, le=250)
    weight_kg: Optional[float] = Field(default=None, ge=20, le=400)  # peso actual (se guarda como medición de hoy)
    age: Optional[int] = Field(default=None, ge=13, le=100)
    sex: Optional[str] = Field(default=None, max_length=10)
    daily_activity: Optional[str] = Field(default=None, max_length=20)
    injuries: Optional[str] = Field(default=None, max_length=500)


class ProfileResponse(ProfileUpdate):
    """Perfil físico + peso actual (última medición) e IMC calculado."""
    bmi: Optional[float] = None


class RoutineGenerationRequest(ProfileUpdate):
    """Todo el intake del instructor: perfil físico + preferencias de entrenamiento."""
    goal: str = Field(default="general", max_length=50)
    days_per_week: int = Field(default=3, ge=1, le=6)
    equipment: Optional[str] = Field(default=None, max_length=50)
    experience: Optional[str] = Field(default=None, max_length=50)
    duration_minutes: Optional[int] = Field(default=60, ge=15, le=180)


class RoutineGenerationResponse(BaseModel):
    ok: bool
    # True cuando el mentor necesita que el cliente elija su tipo de cuerpo primero
    ask_body_type: bool = False
    reply: str
    provider: Optional[str] = None
    routine_id: Optional[int] = None
    routine_name: Optional[str] = None
