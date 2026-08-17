from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.client import Client

router = APIRouter()


async def get_current_client(current_user: User = Depends(get_current_user)):
    """Obtiene (o crea) el perfil de cliente del usuario autenticado."""
    client = await Client.get_or_none(user_id=current_user.id)
    if not client:
        client = await Client.create(
            name=current_user.name,
            email=current_user.email,
            phone=current_user.phone,
            user_id=current_user.id,
        )
    return client


def is_staff(user: User) -> bool:
    return user.role in ("admin", "super_admin", "manager", "receptionist")


# ===============================================================
# Rutinas (lista y creación)
# ===============================================================
@router.get("", response_model=List[schemas.routine.RoutineResponse])
async def get_routines(
    client_id: Optional[int] = Query(None, description="Filtrar por cliente (solo staff)"),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Rutinas del cliente autenticado. El staff puede listar todas o filtrar por cliente."""
    if client_id is not None and is_staff(current_user):
        return await crud.routine.list_all_routines(client_id=client_id, search=search)
    client = await get_current_client(current_user)
    return await crud.routine.get_client_routines(client_id=client.id)


@router.post("", response_model=schemas.routine.RoutineResponse, status_code=201)
async def create_routine(
    routine: schemas.routine.RoutineCreate,
    current_user: User = Depends(get_current_user),
):
    """Crea una rutina. El staff puede asignarla a cualquier cliente; el cliente crea la suya."""
    if routine.client_id is not None and is_staff(current_user):
        target_client = await Client.get_or_none(id=routine.client_id)
        if not target_client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        client_id = target_client.id
    else:
        client = await get_current_client(current_user)
        client_id = client.id
    return await crud.routine.create_routine(
        client_id=client_id, created_by_id=current_user.id, data=routine
    )


# ===============================================================
# Sesiones de entrenamiento (seguimiento)
# NOTA: estas rutas estáticas deben declararse ANTES de /{routine_id}
# para que no sean capturadas por el parámetro de ruta.
# ===============================================================
@router.get("/sessions", response_model=List[schemas.routine.WorkoutSessionResponse])
async def get_my_sessions(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Sesiones recientes del cliente autenticado."""
    client = await get_current_client(current_user)
    return await crud.routine.get_client_sessions(client_id=client.id, limit=limit)


@router.get("/sessions/active")
async def get_active_session(
    routine_id: int = Query(...),
    day_id: int = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Busca una sesión activa para reanudar. Retorna null si no existe."""
    client = await get_current_client(current_user)
    session = await crud.routine.get_active_session(client.id, routine_id, day_id)
    if not session:
        return None
    return session


@router.post("/sessions", response_model=schemas.routine.WorkoutSessionResponse, status_code=201)
async def create_session(
    session: schemas.routine.WorkoutSessionCreate,
    current_user: User = Depends(get_current_user),
):
    """Inicia una nueva sesión de entrenamiento (opcionalmente ligada a una rutina/día)."""
    client = await get_current_client(current_user)
    return await crud.routine.create_session(client_id=client.id, data=session)


@router.get("/sessions/{session_id}", response_model=schemas.routine.WorkoutSessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
):
    session = await crud.routine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    client = await get_current_client(current_user)
    if session.client_id != client.id and not is_staff(current_user):
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


@router.put("/sessions/{session_id}", response_model=schemas.routine.WorkoutSessionResponse)
async def update_session(
    session_id: int,
    session: schemas.routine.WorkoutSessionUpdate,
    current_user: User = Depends(get_current_user),
):
    db_session = await crud.routine.get_session(session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    client = await get_current_client(current_user)
    if db_session.client_id != client.id and not is_staff(current_user):
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return await crud.routine.update_session(session_id, session)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
):
    db_session = await crud.routine.get_session(session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    client = await get_current_client(current_user)
    if db_session.client_id != client.id and not is_staff(current_user):
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    await crud.routine.delete_session(session_id)
    return None


# ===============================================================
# Registro de series
# ===============================================================
@router.post("/sessions/{session_id}/sets", response_model=schemas.routine.SetLogResponse, status_code=201)
async def add_set_log(
    session_id: int,
    set_log: schemas.routine.SetLogCreate,
    current_user: User = Depends(get_current_user),
):
    """Registra (crea o actualiza) una serie dentro de una sesión."""
    db_session = await crud.routine.get_session(session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    client = await get_current_client(current_user)
    if db_session.client_id != client.id and not is_staff(current_user):
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return await crud.routine.upsert_set_log(session_id, set_log)


@router.put("/sets/{log_id}", response_model=schemas.routine.SetLogResponse)
async def update_set_log(
    log_id: int,
    set_log: schemas.routine.SetLogUpdate,
    current_user: User = Depends(get_current_user),
):
    updated = await crud.routine.update_set_log(log_id, set_log)
    if not updated:
        raise HTTPException(status_code=404, detail="Registro de serie no encontrado")
    return updated


@router.delete("/sets/{log_id}", status_code=204)
async def delete_set_log(log_id: int, current_user: User = Depends(get_current_user)):
    deleted = await crud.routine.delete_set_log(log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Registro de serie no encontrado")
    return None


# ===============================================================
# Rutina individual (debe ir DESPUÉS de las rutas estáticas)
# ===============================================================
@router.get("/{routine_id}", response_model=schemas.routine.RoutineResponse)
async def get_routine(
    routine_id: int,
    current_user: User = Depends(get_current_user),
):
    routine = await crud.routine.get_routine(routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    if not is_staff(current_user):
        client = await get_current_client(current_user)
        if routine.client_id != client.id:
            raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return routine


@router.put("/{routine_id}", response_model=schemas.routine.RoutineResponse)
async def update_routine(
    routine_id: int,
    routine: schemas.routine.RoutineUpdate,
    current_user: User = Depends(get_current_user),
):
    db_routine = await crud.routine.get_routine(routine_id)
    if not db_routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    if not is_staff(current_user):
        client = await get_current_client(current_user)
        if db_routine.client_id != client.id:
            raise HTTPException(status_code=404, detail="Rutina no encontrada")
    updated = await crud.routine.update_routine(routine_id, routine)
    return updated


@router.delete("/{routine_id}", status_code=204)
async def delete_routine(
    routine_id: int,
    current_user: User = Depends(get_current_user),
):
    db_routine = await crud.routine.get_routine(routine_id)
    if not db_routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    if not is_staff(current_user):
        client = await get_current_client(current_user)
        if db_routine.client_id != client.id:
            raise HTTPException(status_code=404, detail="Rutina no encontrada")
    await crud.routine.delete_routine(routine_id)
    return None


@router.get("/{routine_id}/sessions", response_model=List[schemas.routine.WorkoutSessionResponse])
async def get_routine_sessions(
    routine_id: int,
    current_user: User = Depends(get_current_user),
):
    routine = await crud.routine.get_routine(routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    client = await get_current_client(current_user)
    if routine.client_id != client.id and not is_staff(current_user):
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return await crud.routine.get_routine_sessions(routine_id)
