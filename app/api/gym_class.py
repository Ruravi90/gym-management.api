from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/", response_model=schemas.GymClass)
async def create_gym_class(
    gym_class: schemas.GymClassCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new gym class (admin only)"""
    if current_user.role not in ("admin", "super_admin", "manager"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.gym_class.create_gym_class(class_data=gym_class.dict())


@router.get("/", response_model=List[schemas.GymClass])
async def read_gym_classes(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    """Get all gym classes"""
    return await crud.gym_class.get_gym_classes(skip=skip, limit=limit)


@router.get("/upcoming", response_model=List[schemas.GymClass])
async def read_upcoming_classes(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    """Get upcoming scheduled classes"""
    return await crud.gym_class.get_upcoming_classes(skip=skip, limit=limit)


@router.get("/{class_id}", response_model=schemas.GymClass)
async def read_gym_class(
    class_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Get a specific gym class"""
    db_class = await crud.gym_class.get_gym_class(class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class


@router.put("/{class_id}", response_model=schemas.GymClass)
async def update_gym_class(
    class_id: int,
    class_update: schemas.GymClassUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update a gym class (admin only)"""
    if current_user.role not in ("admin", "super_admin", "manager"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_class = await crud.gym_class.get_gym_class(class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return await crud.gym_class.update_gym_class(
        class_id=class_id,
        class_update=class_update.dict(exclude_unset=True)
    )


@router.delete("/{class_id}", response_model=schemas.GymClass)
async def delete_gym_class(
    class_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Delete a gym class (admin only)"""
    if current_user.role not in ("admin", "super_admin", "manager"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_class = await crud.gym_class.get_gym_class(class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return await crud.gym_class.delete_gym_class(class_id=class_id)
