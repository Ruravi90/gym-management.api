from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app import crud, models, schemas
from app.utils.auth import get_current_user
from app.database import get_db

from app.models.user import User as UserModel

router = APIRouter()

# Roles allowed to perform administrative actions
ADMIN_ROLES = ("super_admin", "admin", "receptionist")


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, current_user: UserModel = Depends(get_current_user)):
    # Only administrative roles can create system users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_user = await crud.user.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.user.create_user(user=user)


@router.get("/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, current_user: UserModel = Depends(get_current_user)):
    # Only admins/receptionists can list users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    users = await crud.user.get_users(skip=skip, limit=limit)
    return users

@router.get('/me', response_model=schemas.User)
def read_current_user(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    db_user = await crud.user.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Allow viewing own profile or allow administrative roles
    if current_user.id != user_id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return db_user


@router.put('/{user_id}', response_model=schemas.User)
async def update_user(user_id: int, user_update: schemas.UserUpdate, current_user: UserModel = Depends(get_current_user)):
    # Allow users to update their own profile, or administrative roles to update any user
    if current_user.id != user_id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_user = await crud.user.update_user(user_id=user_id, user_update=user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete('/{user_id}', response_model=schemas.User)
async def delete_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    # Only administrative roles can delete users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_user = await crud.user.delete_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch('/{user_id}/role', response_model=schemas.User)
async def change_user_role(user_id: int, role: dict, current_user: UserModel = Depends(get_current_user)):
    # role payload: {"role": "admin"}
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    new_role = role.get('role')
    if not new_role:
        raise HTTPException(status_code=400, detail="Role is required")
    db_user = await crud.user.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.role = new_role
    await db_user.save()
    return db_user


@router.patch('/{user_id}/status', response_model=schemas.User)
async def change_user_status(user_id: int, status_payload: dict, current_user: UserModel = Depends(get_current_user)):
    # status payload: {"status": true}
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    new_status = status_payload.get('status')
    if new_status is None:
        raise HTTPException(status_code=400, detail="Status is required")
    db_user = await crud.user.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.status = bool(new_status)
    await db_user.save()
    return db_user
