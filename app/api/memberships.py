from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=schemas.Membership)
def create_membership(
    membership: schemas.MembershipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow admin users to create memberships
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create memberships"
        )

    # Verify client exists
    client = crud.client.get_client(db, client_id=membership.client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    return crud.membership.create_membership(db=db, membership=membership)

@router.get("/", response_model=List[schemas.Membership])
def read_memberships(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only authorized users can view memberships
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view memberships"
        )
    memberships = crud.membership.get_memberships(db, skip=skip, limit=limit)
    return memberships

@router.get("/statistics", response_model=schemas.MembershipStatistics)
def read_membership_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only authorized users can view membership statistics
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view membership statistics"
        )
    
    # Get various membership statistics
    total_memberships = crud.membership.get_total_memberships_count(db)
    active_memberships = crud.membership.get_active_memberships_count(db)
    expired_memberships = crud.membership.get_expired_memberships_count(db)
    upcoming_expirations = crud.membership.get_upcoming_expirations(db, days=30)  # Next 30 days
    
    return {
        "total_memberships": total_memberships,
        "active_memberships": active_memberships,
        "expired_memberships": expired_memberships,
        "upcoming_expirations": len(upcoming_expirations),
        "upcoming_expirations_list": upcoming_expirations
    }

@router.get("/{membership_id}", response_model=schemas.Membership)
def read_membership(
    membership_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_membership = crud.membership.get_membership(db, membership_id=membership_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Only authorized users can view memberships
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this membership"
        )

    return db_membership

@router.put("/{membership_id}", response_model=schemas.Membership)
def update_membership(
    membership_id: int,
    membership_update: schemas.MembershipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_membership = crud.membership.get_membership(db, membership_id=membership_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Only authorized users can update memberships
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this membership"
        )

    # Verify client exists if client_id is being updated
    if membership_update.client_id:
        client = crud.client.get_client(db, client_id=membership_update.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

    return crud.membership.update_membership(
        db=db,
        membership_id=membership_id,
        membership_update=membership_update
    )

@router.delete("/{membership_id}", response_model=schemas.Membership)
def delete_membership(
    membership_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_membership = crud.membership.get_membership(db, membership_id=membership_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Only admin can delete memberships
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can delete memberships"
        )

    return crud.membership.delete_membership(db=db, membership_id=membership_id)

@router.get("/client/{client_id}", response_model=List[schemas.Membership])
def read_memberships_by_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only authorized users can view client memberships
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this client's memberships"
        )

    # Verify client exists
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    memberships = crud.membership.get_memberships_by_client(db, client_id=client_id)
    return memberships

@router.get("/client/{client_id}/active", response_model=schemas.Membership)
def read_active_membership(
    client_id: int,
    db: Session = Depends(get_db)
):
    # This endpoint is made public to allow the facial check-in kiosk
    # to verify membership status without a logged-in session.

    # Verify client exists
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    membership = crud.membership.get_active_membership(db, client_id=client_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Active membership not found")
    return membership

@router.get("/status/{status}", response_model=List[schemas.Membership])
def read_memberships_by_status(
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only authorized users can view memberships by status
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only authorized users can view memberships by status"
        )
    memberships = crud.membership.get_memberships_by_status(db, status=status)
    return memberships

@router.get("/payment-status/{payment_status}", response_model=List[schemas.Membership])
def read_memberships_by_payment_status(
    payment_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only authorized users can view memberships by payment status
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only authorized users can view memberships by payment status"
        )
    memberships = crud.membership.get_memberships_by_payment_status(db, payment_status=payment_status)
    return memberships

# New endpoints for membership history and statistics
@router.get("/client/{client_id}/history", response_model=List[schemas.Membership])
def read_membership_history(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only authorized users can view client membership history
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this client's membership history"
        )

    # Verify client exists
    client = crud.client.get_client(db, client_id=client_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    
    # Get all memberships for the client (past and present)
    memberships = crud.membership.get_memberships_by_client(db, client_id=client_id)
    return memberships
