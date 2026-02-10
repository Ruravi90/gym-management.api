from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()

# Endpoints específicos para tipos de membresía
@router.get("/", response_model=List[schemas.MembershipType])
async def read_membership_types(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(default=False, description="Filter to show only active membership types"),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all membership types.
    Only authorized users can view membership types.
    """
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view membership types"
        )

    return await crud.membership.get_membership_types(skip=skip, limit=limit, active_only=active_only)


@router.post("/", response_model=schemas.MembershipType)
async def create_membership_type(
    membership_type: schemas.MembershipTypeCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new membership type.
    Only admin and manager users can create membership types.
    """
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create membership types"
        )

    return await crud.membership.create_membership_type(membership_type_data=membership_type.dict())


@router.get("/{membership_type_id}", response_model=schemas.MembershipType)
async def read_membership_type(
    membership_type_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific membership type by ID.
    Only authorized users can view membership types.
    """
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view membership types"
        )

    db_membership_type = await crud.membership.get_membership_type(membership_type_id=membership_type_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return db_membership_type


@router.put("/{membership_type_id}", response_model=schemas.MembershipType)
async def update_membership_type(
    membership_type_id: int,
    membership_type_update: schemas.MembershipTypeUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a membership type.
    Only admin and manager users can update membership types.
    """
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update membership types"
        )

    db_membership_type = await crud.membership.get_membership_type(membership_type_id=membership_type_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return await crud.membership.update_membership_type(
        membership_type_id=membership_type_id,
        membership_type_update=membership_type_update.dict(exclude_unset=True)
    )


@router.delete("/{membership_type_id}", response_model=schemas.MembershipType)
async def delete_membership_type(
    membership_type_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate a membership type (soft delete).
    Only admin users can deactivate membership types.
    """
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can deactivate membership types"
        )

    db_membership_type = await crud.membership.get_membership_type(membership_type_id=membership_type_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return await crud.membership.delete_membership_type(membership_type_id=membership_type_id)