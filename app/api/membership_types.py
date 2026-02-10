from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()

# Endpoints específicos para tipos de membresía
@router.get("/", response_model=List[schemas.MembershipType])
def read_membership_types(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(default=False, description="Filter to show only active membership types"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    return crud.membership.get_membership_types(db, skip=skip, limit=limit, active_only=active_only)


@router.post("/", response_model=schemas.MembershipType)
def create_membership_type(
    membership_type: schemas.MembershipTypeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    return crud.membership.create_membership_type(db=db, membership_type=membership_type)


@router.get("/{membership_type_id}", response_model=schemas.MembershipType)
def read_membership_type(
    membership_type_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    db_membership_type = crud.membership.get_membership_type(db, membership_type_id=membership_type_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return db_membership_type


@router.put("/{membership_type_id}", response_model=schemas.MembershipType)
def update_membership_type(
    membership_type_id: int,
    membership_type_update: schemas.MembershipTypeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    db_membership_type = crud.membership.get_membership_type(db, membership_type_id=membership_type_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return crud.membership.update_membership_type(
        db=db,
        membership_type_id=membership_type_id,
        membership_type_update=membership_type_update
    )


@router.delete("/{membership_type_id}", response_model=schemas.MembershipType)
def delete_membership_type(
    membership_type_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    db_membership_type = crud.membership.get_membership_type(db, membership_type_id=membership_type_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return crud.membership.delete_membership_type(db=db, membership_type_id=membership_type_id)