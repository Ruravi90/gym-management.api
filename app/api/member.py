from fastapi import APIRouter, Depends, HTTPException, status
from app import crud, models, schemas
from app.utils.auth import get_current_user
from app.models.user import User as UserModel
from app.models.client import Client as ClientModel
from typing import List

router = APIRouter()

async def get_current_client(current_user: UserModel = Depends(get_current_user)) -> ClientModel:
    client = await ClientModel.get_or_none(user_id=current_user.id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found for this user"
        )
    return client

@router.get("/me", response_model=schemas.Client)
async def read_member_profile(client: ClientModel = Depends(get_current_client)):
    """Get the current member's profile"""
    return client

@router.get("/attendance", response_model=List[schemas.Attendance])
async def read_member_attendance(client: ClientModel = Depends(get_current_client)):
    """Get the current member's attendance history"""
    return await crud.attendance.get_attendance_by_client(client_id=client.id)

@router.get("/memberships", response_model=List[schemas.Membership])
async def read_member_memberships(client: ClientModel = Depends(get_current_client)):
    """Get the current member's membership history"""
    return await crud.membership.get_memberships_by_client(client_id=client.id)
