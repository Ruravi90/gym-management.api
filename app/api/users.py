from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, models, schemas
from app.database import get_db
from app.utils.auth import get_current_user

from app.models.user import User as UserModel

router = APIRouter()

# Roles allowed to perform administrative actions
ADMIN_ROLES = ("super_admin", "admin", "receptionist")


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Only administrative roles can create system users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_user = crud.user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Only admins/receptionists can list users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users

@router.get('/me', response_model=schemas.User)
def read_current_user(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_user = crud.user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Allow viewing own profile or allow administrative roles
    if current_user.id != user_id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return db_user


@router.put('/{user_id}', response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Allow users to update their own profile, or administrative roles to update any user
    if current_user.id != user_id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_user = crud.user.update_user(db, user_id=user_id, user_update=user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete('/{user_id}', response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Only administrative roles can delete users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_user = crud.user.delete_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch('/{user_id}/role', response_model=schemas.User)
def change_user_role(user_id: int, role: dict, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # role payload: {"role": "admin"}
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    new_role = role.get('role')
    if not new_role:
        raise HTTPException(status_code=400, detail="Role is required")
    db_user = crud.user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.role = new_role
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch('/{user_id}/status', response_model=schemas.User)
def change_user_status(user_id: int, status_payload: dict, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # status payload: {"status": true}
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    new_status = status_payload.get('status')
    if new_status is None:
        raise HTTPException(status_code=400, detail="Status is required")
    db_user = crud.user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.status = bool(new_status)
    db.commit()
    db.refresh(db_user)
    return db_user
