from tortoise.models import Model
from tortoise import fields


class Exercise(Model):
    """Catálogo de ejercicios con GIF/video de demostración."""
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="exercises", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=150)
    description = fields.TextField(null=True)
    muscle_group = fields.CharField(max_length=100, null=True)
    body_part = fields.CharField(max_length=100, null=True)
    equipment = fields.CharField(max_length=100, null=True)
    difficulty = fields.CharField(max_length=20, default="beginner")
    target = fields.CharField(max_length=100, null=True)
    secondary_muscles = fields.CharField(max_length=255, null=True)
    instructions = fields.TextField(null=True)
    tips = fields.TextField(null=True)
    common_mistakes = fields.TextField(null=True)
    modifications = fields.TextField(null=True)
    gif_url = fields.CharField(max_length=500, null=True)
    gif_urls = fields.JSONField(null=True)
    image_url = fields.CharField(max_length=500, null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "exercises"
        indexes = [("muscle_group",), ("is_active",), ("name",)]

    def __str__(self):
        return self.name


class Routine(Model):
    """Rutina asignada a un cliente (puede ser creada por staff o por el propio cliente)."""
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="routines", null=True, on_delete=fields.SET_NULL)
    client = fields.ForeignKeyField("models.Client", related_name="routines", on_delete=fields.CASCADE)
    created_by = fields.ForeignKeyField("models.User", related_name="created_routines", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=150)
    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "routines"
        indexes = [("client_id",), ("is_active",)]

    def __str__(self):
        return self.name


class RoutineDay(Model):
    """Un día de entrenamiento dentro de una rutina (ej. 'Día 1 - Pecho y Tríceps')."""
    id = fields.IntField(pk=True)
    routine = fields.ForeignKeyField("models.Routine", related_name="days", on_delete=fields.CASCADE)
    name = fields.CharField(max_length=100)
    day_of_week = fields.IntField(null=True)  # 0 = lunes ... 6 = domingo (opcional)
    order = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "routine_days"
        indexes = [("routine_id",)]

    def __str__(self):
        return self.name


class RoutineExercise(Model):
    """Ejercicio dentro de un día de rutina con series/reps/peso/descanso."""
    id = fields.IntField(pk=True)
    day = fields.ForeignKeyField("models.RoutineDay", related_name="exercises", on_delete=fields.CASCADE)
    exercise = fields.ForeignKeyField("models.Exercise", related_name="routine_entries", on_delete=fields.CASCADE)
    sets = fields.IntField(default=3)
    reps = fields.CharField(max_length=50, default="10")  # "10", "8-12", "AMRAP"...
    weight = fields.CharField(max_length=50, null=True)   # "20 kg", "barra"...
    rest_seconds = fields.IntField(default=60)
    notes = fields.CharField(max_length=255, null=True)
    order = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "routine_exercises"
        indexes = [("day_id",)]

    def __str__(self):
        return f"{self.exercise_id} en day {self.day_id}"


class WorkoutSession(Model):
    """Sesión de entrenamiento: el seguimiento del cliente al ejecutar un día de rutina."""
    id = fields.IntField(pk=True)
    tenant = fields.ForeignKeyField("models.Tenant", related_name="workout_sessions", null=True, on_delete=fields.SET_NULL)
    client = fields.ForeignKeyField("models.Client", related_name="workout_sessions", on_delete=fields.CASCADE)
    routine = fields.ForeignKeyField("models.Routine", related_name="sessions", null=True, on_delete=fields.SET_NULL)
    day = fields.ForeignKeyField("models.RoutineDay", related_name="sessions", null=True, on_delete=fields.SET_NULL)
    date = fields.DateField()
    notes = fields.TextField(null=True)
    status = fields.CharField(max_length=20, default="in_progress")  # in_progress, completed
    duration_minutes = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "workout_sessions"
        indexes = [("client_id", "date"), ("routine_id",)]

    def __str__(self):
        return f"Sesión {self.id} - {self.date}"


class SetLog(Model):
    """Registro de cada serie realizada en una sesión (reps, peso, completada)."""
    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField("models.WorkoutSession", related_name="set_logs", on_delete=fields.CASCADE)
    exercise = fields.ForeignKeyField("models.Exercise", related_name="set_logs", on_delete=fields.CASCADE)
    set_number = fields.IntField()
    reps = fields.IntField(null=True)
    weight = fields.CharField(max_length=50, null=True)
    completed = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "set_logs"
        indexes = [("session_id",)]

    def __str__(self):
        return f"Serie {self.set_number} del ejercicio {self.exercise_id}"
