from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app import crud, schemas
from app.utils.security import AuthenticatedUser, ReceptionistOrAbove

router = APIRouter()

TRAINING_TYPES = {"gym", "calisthenics", "crossfit"}
DIFFICULTIES = {"beginner", "intermediate", "advanced"}


@router.get("/options")
async def exercise_options(current_user = AuthenticatedUser):
    """Opciones oficiales para construir filtros en cualquier cliente."""
    return {
        "training_types": [
            {"value": "gym", "label": "Gimnasio"},
            {"value": "calisthenics", "label": "Calistenia"},
            {"value": "crossfit", "label": "CrossFit"},
        ],
        "difficulties": [
            {"value": "beginner", "label": "Principiante"},
            {"value": "intermediate", "label": "Intermedio"},
            {"value": "advanced", "label": "Avanzado"},
        ],
    }


@router.get("", response_model=List[schemas.routine.ExerciseResponse])
async def list_exercises(
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    muscle_group: Optional[str] = Query(None, description="Grupo muscular (chest, back, shoulders...)"),
    equipment: Optional[str] = Query(None, description="Equipamiento (barbell, dumbbell, body weight...)"),
    training_type: Optional[str] = Query(None, description="Modalidad (gym, calisthenics, crossfit)"),
    difficulty: Optional[str] = Query(None, description="Nivel (beginner, intermediate, advanced)"),
    current_user = AuthenticatedUser,
):
    """Lista el catálogo de ejercicios (público para usuarios autenticados)."""
    if training_type and training_type not in TRAINING_TYPES:
        raise HTTPException(status_code=400, detail="Modalidad inválida")
    if difficulty and difficulty not in DIFFICULTIES:
        raise HTTPException(status_code=400, detail="Dificultad inválida")
    return await crud.routine.list_exercises(
        search=search, muscle_group=muscle_group, equipment=equipment, training_type=training_type,
        difficulty=difficulty
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
