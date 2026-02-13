from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app import crud, models, schemas
from app.utils.auth import get_current_user


from app.models.user import User as UserModel

router = APIRouter()

# Roles allowed to perform administrative actions
ADMIN_ROLES = ("super_admin", "admin")


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, current_user: UserModel = Depends(get_current_user)):
    # Only administrative roles can create system users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para crear usuarios")
    
    # Non-super_admin cannot create super_admin
    if user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para crear un Super Admin")

    db_user = await crud.user.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.user.create_user(user_data=user.dict())


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
    # Any user can update their own profile, or administrative roles can update others
    if current_user.id != user_id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para editar este usuario")

    db_user = await crud.user.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Protection for Super Admin
    if db_user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para modificar a un Super Admin")

    # Role escalation protection
    if hasattr(user_update, 'role') and user_update.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para asignar el rol Super Admin")

    # Convert Pydantic model to dict for CRUD operations
    if hasattr(user_update, 'model_dump'):
        user_update_dict = user_update.model_dump(exclude_unset=True)
    elif hasattr(user_update, 'dict'):
        user_update_dict = user_update.dict(exclude_unset=True)
    else:
        user_update_dict = user_update

    return await crud.user.update_user(user_id=user_id, user_update=user_update_dict)


@router.delete('/{user_id}', response_model=schemas.User)
async def delete_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    # Only administrative roles can delete users
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para eliminar usuarios")
    
    db_user = await crud.user.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Protection for Super Admin
    if db_user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para eliminar a un Super Admin")

    await crud.user.delete_user(user_id=user_id)
    return db_user


@router.patch('/{user_id}/role', response_model=schemas.User)
async def change_user_role(user_id: int, role: dict, current_user: UserModel = Depends(get_current_user)):
    # role payload: {"role": "admin"}
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar roles")
    
    new_role = role.get('role')
    if not new_role:
        raise HTTPException(status_code=400, detail="El rol es obligatorio")
        
    db_user = await crud.user.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Protection for Super Admin target
    if db_user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar el rol de un Super Admin")

    # Role escalation protection (cannot make someone super_admin)
    if new_role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para asignar el rol Super Admin")

    db_user.role = new_role
    await db_user.save()
    return db_user


@router.patch('/{user_id}/status', response_model=schemas.User)
async def change_user_status(user_id: int, status_payload: dict, current_user: UserModel = Depends(get_current_user)):
    # status payload: {"status": true}
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar el estado de usuarios")
        
    new_status = status_payload.get('status')
    if new_status is None:
        raise HTTPException(status_code=400, detail="El estado es obligatorio")
        
    db_user = await crud.user.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Protection for Super Admin target
    if db_user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar el estado de un Super Admin")

    db_user.status = bool(new_status)
    await db_user.save()
    return db_user
