from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app import crud, schemas
from app.utils.security import AuthenticatedUser, ReceptionistOrAbove

router = APIRouter()


@router.get("", response_model=List[schemas.routine.ExerciseResponse])
async def list_exercises(
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    muscle_group: Optional[str] = Query(None, description="Grupo muscular (chest, back, shoulders...)"),
    equipment: Optional[str] = Query(None, description="Equipamiento (barbell, dumbbell, body weight...)"),
    current_user = AuthenticatedUser,
):
    """Lista el catálogo de ejercicios (público para usuarios autenticados)."""
    return await crud.routine.list_exercises(
        search=search, muscle_group=muscle_group, equipment=equipment
    )


@router.get("/{exercise_id}", response_model=schemas.routine.ExerciseResponse)
async def get_exercise(exercise_id: int, current_user = AuthenticatedUser):
    exercise = await crud.routine.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    return exercise


@router.post("", response_model=schemas.routine.ExerciseResponse, status_code=201)
async def create_exercise(
    exercise: schemas.routine.ExerciseCreate,
    current_user = ReceptionistOrAbove,
):
    """Crea un ejercicio en el catálogo (staff)."""
    return await crud.routine.create_exercise(exercise)


@router.put("/{exercise_id}", response_model=schemas.routine.ExerciseResponse)
async def update_exercise(
    exercise_id: int,
    exercise: schemas.routine.ExerciseUpdate,
    current_user = ReceptionistOrAbove,
):
    updated = await crud.routine.update_exercise(exercise_id, exercise)
    if not updated:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    return updated


@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(exercise_id: int, current_user = ReceptionistOrAbove):
    deleted = await crud.routine.delete_exercise(exercise_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    return None
