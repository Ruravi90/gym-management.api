from fastapi import APIRouter, Depends
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.client import Client
from app.services import mentor as mentor_service

router = APIRouter()


async def get_current_client(current_user: User = Depends(get_current_user)):
    client = await Client.get_or_none(user_id=current_user.id)
    if not client:
        client = await Client.create(
            name=current_user.name,
            email=current_user.email,
            phone=current_user.phone,
            user_id=current_user.id,
        )
    return client


async def _build_context(client: Client) -> str:
    routines = await crud.routine.get_client_routines(client_id=client.id, active_only=False)
    recent_sessions = await crud.routine.get_client_sessions(client_id=client.id, limit=10)
    measurements = await crud.measurement.list_measurements(client_id=client.id, limit=4)
    return mentor_service.build_client_context(client, routines, recent_sessions, measurements)


@router.post("/chat", response_model=schemas.routine.MentorResponse)
async def mentor_chat(
    request: schemas.routine.MentorRequest,
    current_user: User = Depends(get_current_user),
):
    """Chatea con el mentor IA. Usa la rutina, el progreso y las medidas del cliente como contexto."""
    client = await get_current_client(current_user)
    context = await _build_context(client)
    result = await mentor_service.mentor_chat(request.message, context)
    return schemas.routine.MentorResponse(**result)


@router.post("/weekly-checkin", response_model=schemas.routine.MentorResponse)
async def weekly_checkin(
    current_user: User = Depends(get_current_user),
):
    """Genera el reporte semanal: medidas vs semana anterior + adherencia a la rutina + recomendaciones."""
    client = await get_current_client(current_user)
    context = await _build_context(client)
    result = await mentor_service.weekly_checkin(context)
    return schemas.routine.MentorResponse(**result)
