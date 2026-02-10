from functools import wraps
from fastapi import Depends, HTTPException, status
from app.utils.auth import get_current_user
from app.models.user import User, UserRoleEnum

def require_role(required_roles=None):
    """
    Dependency to require specific roles for accessing endpoints.
    If required_roles is None, any authenticated user can access.
    """
    if required_roles is None:
        required_roles = [UserRoleEnum.USER, UserRoleEnum.ADMIN]
    
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency to require admin or super_admin role for accessing endpoints.
    """
    if current_user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_authenticated_user(current_user: User = Depends(get_current_user)):
    """
    Dependency to require any authenticated user.
    """
    return current_user

# Pre-defined reusable dependencies
AdminOnly = Depends(require_admin)
ManagerOrAbove = Depends(require_role([UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN, UserRoleEnum.MANAGER]))
ReceptionistOrAbove = Depends(require_role([
    UserRoleEnum.ADMIN, 
    UserRoleEnum.SUPER_ADMIN, 
    UserRoleEnum.MANAGER, 
    UserRoleEnum.RECEPTIONIST
]))
AuthenticatedUser = Depends(require_authenticated_user)