from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.client import Client

router = APIRouter()


async def get_current_client(current_user: User = Depends(get_current_user)):
    client = await Client.get_or_none(user_id=current_user.id)
    if not client:
        tenant_id = getattr(current_user, 'tenant_id', None)
        client = await Client.create(
            name=current_user.name,
            email=current_user.email,
            phone=current_user.phone,
            user_id=current_user.id,
            tenant_id=tenant_id,
        )
    return client


def is_staff(user: User) -> bool:
    return user.role in ("admin", "super_admin", "manager", "receptionist")


@router.get("", response_model=List[schemas.measurement.BodyMeasurementResponse])
async def get_measurements(
    limit: int = Query(100, ge=1, le=500),
    client_id: int = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Medidas de un cliente. Staff puede pasar client_id para ver las de cualquier cliente."""
    if client_id and is_staff(current_user):
        target_client_id = client_id
    else:
        client = await get_current_client(current_user)
        target_client_id = client.id
    return await crud.measurement.list_measurements(client_id=target_client_id, limit=limit)


@router.post("", response_model=schemas.measurement.BodyMeasurementResponse, status_code=201)
async def create_measurement(
    measurement: schemas.measurement.BodyMeasurementCreate,
    client_id: int = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Registra (o actualiza) las medidas de una fecha. Una entrada por fecha.
    Staff puede pasar client_id para registrar medidas de otro cliente."""
    if client_id and is_staff(current_user):
        target_client_id = client_id
    else:
        client = await get_current_client(current_user)
        target_client_id = client.id
    result = await crud.measurement.upsert_measurement(client_id=target_client_id, data=measurement)

    # Gamification: award XP for registering measurements
    try:
        from app.services.gamification import GamificationService
        gamification = GamificationService()
        await gamification.award_xp(target_client_id, "measurement_logged", 5, "Medidas corporales registradas")
    except Exception:
        pass

    return result


@router.put("/{measurement_id}", response_model=schemas.measurement.BodyMeasurementResponse)
async def update_measurement(
    measurement_id: int,
    measurement: schemas.measurement.BodyMeasurementUpdate,
    current_user: User = Depends(get_current_user),
):
    db_measurement = await crud.measurement.get_measurement(measurement_id)
    if not db_measurement:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    if not is_staff(current_user):
        client = await get_current_client(current_user)
        if db_measurement.client_id != client.id:
            raise HTTPException(status_code=404, detail="Medición no encontrada")
    return await crud.measurement.update_measurement(measurement_id, measurement)


@router.delete("/{measurement_id}", status_code=204)
async def delete_measurement(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
):
    db_measurement = await crud.measurement.get_measurement(measurement_id)
    if not db_measurement:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    if not is_staff(current_user):
        client = await get_current_client(current_user)
        if db_measurement.client_id != client.id:
            raise HTTPException(status_code=404, detail="Medición no encontrada")
    await crud.measurement.delete_measurement(measurement_id)
    return None
