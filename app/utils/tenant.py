from fastapi import Depends, HTTPException, status
from app.utils.auth import get_current_user
from app.models.user import User, UserRoleEnum
from app.models.tenant import Tenant


def require_super_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRoleEnum.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere acceso de Super Admin"
        )
    return current_user


def require_tenant_user(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRoleEnum.SUPER_ADMIN:
        return current_user
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no asignado a un tenant"
        )
    return current_user


def get_current_tenant_id(current_user: User = Depends(get_current_user)) -> int:
    if current_user.role == UserRoleEnum.SUPER_ADMIN:
        return None
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no asignado a un tenant"
        )
    return current_user.tenant_id
