from fastapi import APIRouter, Depends, HTTPException, status
from app import crud, models, schemas
from app.utils.auth import get_current_client as get_authenticated_client
from app.models.client import Client as ClientModel
from typing import List

router = APIRouter()

get_current_client = get_authenticated_client

@router.get("/me", response_model=schemas.Client)
async def read_member_profile(client: ClientModel = Depends(get_current_client)):
    """Get the current member's profile"""
    return client


@router.get("/profile", response_model=schemas.Client)
async def get_member_profile(client: ClientModel = Depends(get_current_client)):
    """Obtiene los datos editables del socio autenticado."""
    # Compatibilidad con datos antiguos: el contrato del portal usa claves
    # estables, no las etiquetas traducidas que se muestran en la UI.
    aliases = {"ectomorfo": "ectomorph", "mesomorfo": "mesomorph", "endomorfo": "endomorph"}
    canonical_body_type = aliases.get((client.body_type or "").strip().lower())
    if canonical_body_type and canonical_body_type != client.body_type:
        client.body_type = canonical_body_type
        await client.save(update_fields=["body_type", "updated_at"])
    return client


@router.put("/profile", response_model=schemas.Client)
async def update_member_profile(
    payload: schemas.MemberProfileUpdate,
    client: ClientModel = Depends(get_current_client),
):
    """Actualiza únicamente el perfil del socio autenticado."""
    data = payload.model_dump(exclude_unset=True)

    if "body_type" in data and data["body_type"] is not None:
        data["body_type"] = data["body_type"].strip().lower()
        if data["body_type"] not in {"ectomorph", "mesomorph", "endomorph"}:
            raise HTTPException(status_code=422, detail="Tipo de cuerpo inválido")

    if "email" in data and data["email"] != client.email:
        if await ClientModel.filter(email=data["email"]).exclude(id=client.id).exists():
            raise HTTPException(status_code=409, detail="El correo electrónico ya está registrado")

    if not data:
        return client

    for field, value in data.items():
        setattr(client, field, value)
    await client.save(update_fields=list(data.keys()) + ["updated_at"])
    return client

@router.get("/attendance", response_model=List[schemas.Attendance])
async def read_member_attendance(client: ClientModel = Depends(get_current_client)):
    """Get the current member's attendance history"""
    return await crud.attendance.get_attendance_by_client(client_id=client.id)

@router.get("/memberships", response_model=List[schemas.Membership])
async def read_member_memberships(client: ClientModel = Depends(get_current_client)):
    """Get the current member's membership history"""
    return await crud.membership.get_memberships_by_client(client_id=client.id)
