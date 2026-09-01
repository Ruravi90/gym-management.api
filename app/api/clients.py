from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from app import crud, models, schemas
from app.services.facial_recognition import FacialRecognitionService
from app.utils.auth import get_current_user

from app.models.user import User as UserModel
from app.models.user import UserRoleEnum
from app.utils.auth import hash_password
import secrets

from app.utils.logging import logger
from app.services.billing_limits import ensure_within_limit

router = APIRouter()

_face_service = None

def get_face_service() -> FacialRecognitionService:
    global _face_service
    if _face_service is None:
        _face_service = FacialRecognitionService()
    return _face_service

@router.post("", response_model=schemas.Client)
async def create_client(client: schemas.ClientCreate, current_user: UserModel = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    await ensure_within_limit(tenant_id, "clients")

    if client.email:
        db_client = await crud.client.get_client_by_email(email=client.email, tenant_id=tenant_id)
        if db_client:
            raise HTTPException(status_code=400, detail="Email already registered")

    if client.phone:
        db_client = await crud.client.get_client_by_phone(phone=client.phone, tenant_id=tenant_id)
        if db_client:
            raise HTTPException(status_code=400, detail="Phone already registered")
            
    return await crud.client.create_client(
        client_data=client.dict(),
        # The client profile must not point to the staff user creating it.
        user_id=None,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )

@router.get("", response_model=List[schemas.Client])
async def read_clients(skip: int = 0, limit: int = 100, current_user: UserModel = Depends(get_current_user)):
    try:
        tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
        logger.debug(f"accessing read_clients. User: {current_user.email}, Skip: {skip}, Limit: {limit}, tenant_id: {tenant_id}")
        clients = await crud.client.get_clients(skip=skip, limit=limit, tenant_id=tenant_id)
        logger.debug(f"retrieved {len(clients)} clients")
        return clients
    except Exception as e:
        logger.error(f"ERROR in read_clients: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/search/", response_model=List[schemas.Client])
async def search_clients(search: str, skip: int = 0, limit: int = 100, current_user: UserModel = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    clients = await crud.client.search_clients(search_term=search, skip=skip, limit=limit, tenant_id=tenant_id)
    return clients

@router.get("/{client_id}", response_model=schemas.Client)
async def read_client(client_id: int, current_user: UserModel = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    db_client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.put("/{client_id}", response_model=schemas.Client)
async def update_client(client_id: int, client_update: schemas.ClientUpdate, current_user: UserModel = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    db_client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    profile_fields = {"birth_date", "body_type", "height_cm", "sex", "injuries", "goal", "restrictions", "emergency_contact"}
    update_data = client_update.dict(exclude_unset=True)
    profile = {key: update_data.pop(key) for key in list(update_data) if key in profile_fields}
    if profile:
        user = await UserModel.get_or_none(id=db_client.user_id) if db_client.user_id else None
        # Legacy records may point to the staff user. Never overwrite staff profile data.
        if not user or user.role != UserRoleEnum.USER:
            user = await UserModel.create(
                name=db_client.name,
                # Client.email is the contact email and may already belong to
                # another account; User.email is globally unique.
                email=None,
                phone=db_client.phone,
                role=UserRoleEnum.USER,
                hashed_password=hash_password(secrets.token_urlsafe(32)),
                tenant_id=db_client.tenant_id,
            )
            db_client.user_id = user.id
            await db_client.save(update_fields=["user_id", "updated_at"])
        await user.update_from_dict(profile)
        await user.save()
    return await crud.client.update_client(
        client_id=client_id,
        client_update=update_data,
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )

@router.delete("/{client_id}", response_model=schemas.Client)
async def delete_client(client_id: int, current_user: UserModel = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    db_client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return await crud.client.delete_client(
        client_id=client_id,
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )

@router.post("/{client_id}/face")
async def register_face(client_id: int, file: UploadFile = File(...), current_user: UserModel = Depends(get_current_user)):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    content = await file.read()
    try:
        success = await get_face_service().register_face(client_id, content)
        return {"status": "success", "message": "Face registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{client_id}/face")
async def get_face_registration_status(client_id: int, current_user: UserModel = Depends(get_current_user)):
    """Check if client has registered their face"""
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    facial_encoding = await crud.facial_encoding.get_facial_encoding_by_client(client_id=client_id)
    if facial_encoding:
        return {"registered": True, "message": "Face is registered"}
    else:
        return {"registered": False, "message": "Face is not registered"}

@router.delete("/{client_id}/face")
async def remove_face_registration(client_id: int, current_user: UserModel = Depends(get_current_user)):
    """Remove face registration for a client"""
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    facial_encoding = await crud.facial_encoding.delete_facial_encoding(client_id=client_id)
    if facial_encoding:
        return {"status": "success", "message": "Face registration removed"}
    else:
        raise HTTPException(status_code=404, detail="Face registration not found")
