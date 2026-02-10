from functools import wraps
from fastapi import Depends, HTTPException, status
from app.utils.auth import get_current_user
from app.models.user import User

def require_role(required_roles=None):
    """
    Decorator to require specific roles for accessing endpoints.
    If required_roles is None, any authenticated user can access.
    """
    if required_roles is None:
        required_roles = ["user", "admin"]  # Default to any authenticated user
    
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.membership_type not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_user)):
    """
    Decorator to require admin role for accessing endpoints.
    """
    if current_user.membership_type != "VIP":  # Assuming VIP has admin privileges
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_authenticated_user(current_user: User = Depends(get_current_user)):
    """
    Decorator to require any authenticated user.
    """
    return current_user