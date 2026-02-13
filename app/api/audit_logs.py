from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app import crud, schemas, models
from app.utils.auth import get_current_user
from app.models.user import UserRoleEnum

# Debug log to see if this file is being loaded
print("Loading audit_logs API module...")

router = APIRouter()

@router.get("/", response_model=List[schemas.AuditLog])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    user_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    action_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user = Depends(get_current_user)
):
    """
    Retrieve audit logs with optional filters.
    """
    # Only admins and managers should be able to view audit logs
    if current_user.role not in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.ADMIN, UserRoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Convert action_type string to enum if provided
    action_type_enum = None
    if action_type:
        try:
            action_type_enum = schemas.ActionTypeEnum(action_type.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid action type: {action_type}")
    
    audit_logs = await crud.audit_log.get_audit_logs(
        skip=skip,
        limit=limit,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action_type=action_type_enum,
        start_date=start_date,
        end_date=end_date
    )
    return audit_logs


@router.get("/{audit_log_id}", response_model=schemas.AuditLog)
async def get_audit_log(
    audit_log_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get a specific audit log entry.
    """
    # Only admins and managers should be able to view audit logs
    if current_user.role not in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.ADMIN, UserRoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_audit_log = await crud.audit_log.get_audit_log(audit_log_id)
    if not db_audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return db_audit_log


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[schemas.AuditLog])
async def get_audit_logs_by_entity(
    entity_type: str,
    entity_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get all audit logs for a specific entity.
    """
    # Only admins and managers should be able to view audit logs
    if current_user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    audit_logs = await crud.audit_log.get_audit_logs_by_entity(
        entity_type=entity_type,
        entity_id=entity_id
    )
    return audit_logs

@router.get("/user/{user_id}", response_model=List[schemas.AuditLog])
async def get_audit_logs_by_user(
    user_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get all audit logs performed by a specific user.
    """
    # Only admins and managers should be able to view audit logs
    if current_user.role not in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.ADMIN, UserRoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Users can view their own audit logs
    if current_user.role not in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.ADMIN, UserRoleEnum.MANAGER] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    audit_logs = await crud.audit_log.get_audit_logs_by_user(user_id=user_id)
    return audit_logs