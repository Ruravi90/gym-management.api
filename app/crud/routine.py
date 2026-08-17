from typing import List, Optional
from datetime import date as date_cls
from fastapi import HTTPException
from app.models.routine import (
    Exercise, Routine, RoutineDay, RoutineExercise, WorkoutSession, SetLog,
)
from app.schemas.routine import (
    ExerciseCreate, ExerciseUpdate,
    RoutineCreate, RoutineUpdate,
    WorkoutSessionCreate, WorkoutSessionUpdate,
    SetLogCreate, SetLogUpdate,
)


# ===============================================================
# Exercises
# ===============================================================
async def list_exercises(
    search: Optional[str] = None,
    muscle_group: Optional[str] = None,
    equipment: Optional[str] = None,
    include_inactive: bool = False,
) -> List[Exercise]:
    qs = Exercise.all()
    if not include_inactive:
        qs = qs.filter(is_active=True)
    if muscle_group:
        qs = qs.filter(muscle_group=muscle_group)
    if equipment:
        qs = qs.filter(equipment=equipment)
    if search:
        qs = qs.filter(name__icontains=search)
    return await qs.order_by("name")


async def get_exercise(exercise_id: int) -> Optional[Exercise]:
    return await Exercise.get_or_none(id=exercise_id)


async def create_exercise(data: ExerciseCreate) -> Exercise:
    return await Exercise.create(**data.model_dump())


async def update_exercise(exercise_id: int, data: ExerciseUpdate) -> Optional[Exercise]:
    exercise = await Exercise.get_or_none(id=exercise_id)
    if not exercise:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await exercise.update_from_dict(update_data)
        await exercise.save()
    return exercise


async def delete_exercise(exercise_id: int) -> bool:
    exercise = await Exercise.get_or_none(id=exercise_id)
    if not exercise:
        return False
    await exercise.delete()
    return True


# ===============================================================
# Routines
# ===============================================================
async def _load_routine(routine_id: int) -> Optional[Routine]:
    return await Routine.get_or_none(id=routine_id).prefetch_related(
        "days__exercises__exercise"
    )


async def get_client_routines(client_id: int, active_only: bool = False) -> List[Routine]:
    qs = Routine.filter(client_id=client_id)
    if active_only:
        qs = qs.filter(is_active=True)
    return await qs.order_by("-created_at").prefetch_related("days__exercises__exercise")


async def get_routine(routine_id: int) -> Optional[Routine]:
    return await _load_routine(routine_id)


async def list_all_routines(
    client_id: Optional[int] = None,
    search: Optional[str] = None,
) -> List[Routine]:
    qs = Routine.all()
    if client_id:
        qs = qs.filter(client_id=client_id)
    if search:
        qs = qs.filter(name__icontains=search)
    return await qs.order_by("-created_at").prefetch_related("days__exercises__exercise", "client")


async def create_routine(client_id: int, created_by_id: Optional[int], data: RoutineCreate) -> Routine:
    routine = await Routine.create(
        client_id=client_id,
        created_by_id=created_by_id,
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    await _replace_days(routine, data.days)
    return await _load_routine(routine.id)


async def update_routine(routine_id: int, data: RoutineUpdate) -> Optional[Routine]:
    routine = await Routine.get_or_none(id=routine_id)
    if not routine:
        return None

    update_data = data.model_dump(exclude_unset=True, exclude={"days"})
    if update_data:
        await routine.update_from_dict(update_data)
        await routine.save()

    if data.days is not None:
        await _replace_days(routine, data.days)

    return await _load_routine(routine_id)


async def delete_routine(routine_id: int) -> bool:
    routine = await Routine.get_or_none(id=routine_id)
    if not routine:
        return False
    await routine.delete()
    return True


async def _replace_days(routine: Routine, days: List) -> None:
    """Reemplaza los días (y sus ejercicios) de una rutina. Idempotente: borra y recrea."""
    await RoutineDay.filter(routine_id=routine.id).delete()

    for i, day_data in enumerate(days):
        day = await RoutineDay.create(
            routine_id=routine.id,
            name=day_data.name,
            day_of_week=day_data.day_of_week,
            order=day_data.order if day_data.order else i,
        )
        for j, ex_data in enumerate(day_data.exercises):
            exercise = await Exercise.get_or_none(id=ex_data.exercise_id)
            if not exercise:
                raise HTTPException(status_code=404, detail=f"Ejercicio {ex_data.exercise_id} no encontrado")
            await RoutineExercise.create(
                day_id=day.id,
                exercise_id=ex_data.exercise_id,
                sets=ex_data.sets,
                reps=ex_data.reps,
                weight=ex_data.weight,
                rest_seconds=ex_data.rest_seconds,
                notes=ex_data.notes,
                order=ex_data.order if ex_data.order else j,
            )


# ===============================================================
# Workout sessions + set logs
# ===============================================================
async def _load_session(session_id: int) -> Optional[WorkoutSession]:
    return await WorkoutSession.get_or_none(id=session_id).prefetch_related(
        "set_logs__exercise", "day__exercises__exercise"
    )


async def get_client_sessions(client_id: int, limit: int = 30) -> List[WorkoutSession]:
    return await WorkoutSession.filter(client_id=client_id).order_by("-date", "-id").limit(limit).prefetch_related(
        "set_logs__exercise", "day__exercises__exercise"
    )


async def get_routine_sessions(routine_id: int) -> List[WorkoutSession]:
    return await WorkoutSession.filter(routine_id=routine_id).order_by("-date", "-id").prefetch_related(
        "set_logs__exercise", "day__exercises__exercise"
    )


async def get_session(session_id: int) -> Optional[WorkoutSession]:
    return await _load_session(session_id)


async def get_active_session(client_id: int, routine_id: int, day_id: int) -> Optional[WorkoutSession]:
    session = await WorkoutSession.filter(
        client_id=client_id,
        routine_id=routine_id,
        day_id=day_id,
        status="pending",
    ).order_by("-id").first()
    if session:
        return await _load_session(session.id)
    return None


async def create_session(client_id: int, data: WorkoutSessionCreate) -> WorkoutSession:
    # Evitar duplicados: si ya hay una sesión pending para ese día, reusarla
    existing = await WorkoutSession.filter(
        client_id=client_id,
        routine_id=data.routine_id,
        day_id=data.day_id,
        status="pending",
    ).order_by("-id").first()
    if existing:
        return await _load_session(existing.id)

    session = await WorkoutSession.create(
        client_id=client_id,
        routine_id=data.routine_id,
        day_id=data.day_id,
        notes=data.notes,
        date=date_cls.today(),
    )
    return await _load_session(session.id)


async def update_session(session_id: int, data: WorkoutSessionUpdate) -> Optional[WorkoutSession]:
    session = await WorkoutSession.get_or_none(id=session_id)
    if not session:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await session.update_from_dict(update_data)
        await session.save()
    return await _load_session(session_id)


async def delete_session(session_id: int) -> bool:
    session = await WorkoutSession.get_or_none(id=session_id)
    if not session:
        return False
    await session.delete()
    return True


async def upsert_set_log(session_id: int, data: SetLogCreate) -> SetLog:
    """Crea o actualiza el registro de una serie (identificada por exercise_id + set_number)."""
    session = await WorkoutSession.get_or_none(id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    exercise = await Exercise.get_or_none(id=data.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    log, created = await SetLog.update_or_create(
        session_id=session_id,
        exercise_id=data.exercise_id,
        set_number=data.set_number,
        defaults={
            "reps": data.reps,
            "weight": data.weight,
            "completed": data.completed,
        },
    )
    await log.fetch_related("exercise")
    return log


async def update_set_log(log_id: int, data: SetLogUpdate) -> Optional[SetLog]:
    log = await SetLog.get_or_none(id=log_id)
    if not log:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await log.update_from_dict(update_data)
        await log.save()
    await log.fetch_related("exercise")
    return log


async def delete_set_log(log_id: int) -> bool:
    log = await SetLog.get_or_none(id=log_id)
    if not log:
        return False
    await log.delete()
    return True
