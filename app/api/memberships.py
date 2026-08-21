from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app import crud
from app.schemas import membership as schemas
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.membership import Membership, MembershipType

router = APIRouter()


@router.post("", response_model=schemas.Membership)
async def create_membership(
    membership: schemas.MembershipCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new membership.
    Only admin and manager users can create memberships.
    """
    # Only allow admin users to create memberships
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create memberships"
        )

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    # Verify client exists
    client = await crud.client.get_client(membership.client_id, tenant_id=tenant_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if client already has an active membership
    active_membership = await crud.membership.get_active_membership(membership.client_id, tenant_id=tenant_id)
    if active_membership:
        raise HTTPException(
            status_code=400, 
            detail="El cliente ya tiene una membresía activa. Por favor, expire o cancele la membresía actual antes de agregar una nueva."
        )

    return await crud.membership.create_membership(
        membership.dict(),
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )


@router.get("", response_model=List[schemas.Membership])
async def read_memberships(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    # Only authorized users can view memberships
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view memberships"
        )
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    memberships = await crud.membership.get_memberships(skip=skip, limit=limit, tenant_id=tenant_id)
    return memberships


@router.get("/statistics", response_model=schemas.MembershipStatistics)
async def read_membership_statistics(
    current_user: User = Depends(get_current_user)
):
    # Only authorized users can view membership statistics
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view membership statistics"
        )

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    # Get various membership statistics
    total_memberships = await crud.membership.get_total_memberships_count(tenant_id=tenant_id)
    active_memberships = await crud.membership.get_active_memberships_count(tenant_id=tenant_id)
    expired_memberships = await crud.membership.get_expired_memberships_count(tenant_id=tenant_id)
    upcoming_expirations = await crud.membership.get_upcoming_expirations(days=30, tenant_id=tenant_id)

    return {
        "total_memberships": total_memberships,
        "active_memberships": active_memberships,
        "expired_memberships": expired_memberships,
        "upcoming_expirations": len(upcoming_expirations),
        "upcoming_expirations_list": upcoming_expirations
    }


@router.get("/{membership_id}", response_model=schemas.Membership)
async def read_membership(
    membership_id: int,
    current_user: User = Depends(get_current_user)
):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    db_membership = await crud.membership.get_membership(membership_id=membership_id, tenant_id=tenant_id)
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
async def update_membership(
    membership_id: int,
    membership_update: schemas.MembershipUpdate,
    current_user: User = Depends(get_current_user)
):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    db_membership = await crud.membership.get_membership(membership_id=membership_id, tenant_id=tenant_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Only authorized users can update memberships
    if current_user.role not in ["admin", "manager", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this membership"
        )

    return await crud.membership.update_membership(
        membership_id=membership_id,
        membership_update=membership_update.dict(exclude_unset=True),
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )


@router.delete("/{membership_id}", response_model=schemas.Membership)
async def delete_membership(
    membership_id: int,
    current_user: User = Depends(get_current_user)
):
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    db_membership = await crud.membership.get_membership(membership_id=membership_id, tenant_id=tenant_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Only admin can delete memberships
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can delete memberships"
        )

    return await crud.membership.delete_membership(
        membership_id=membership_id,
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )


@router.get("/client/{client_id}", response_model=List[schemas.Membership])
async def read_memberships_by_client(
    client_id: int,
    current_user: User = Depends(get_current_user)
):
    # Only authorized users can view client memberships
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this client's memberships"
        )

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    # Verify client exists
    client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    memberships = await crud.membership.get_memberships_by_client(client_id=client_id, tenant_id=tenant_id)
    return memberships


@router.get("/client/{client_id}/active", response_model=schemas.Membership)
async def read_active_membership(
    client_id: int,
    current_user: User = Depends(get_current_user)
):
    # This endpoint was public for the facial check-in kiosk, now requires auth for tenant scoping
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    # Verify client exists
    client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")
    membership = await crud.membership.get_active_membership(client_id=client_id, tenant_id=tenant_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Active membership not found")
    return membership


@router.get("/status/{status}", response_model=List[schemas.Membership])
async def read_memberships_by_status(
    status: str,
    current_user: User = Depends(get_current_user)
):
    # Only authorized users can view memberships by status
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only authorized users can view memberships by status"
        )
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    memberships = await crud.membership.get_memberships_by_status(status=status, tenant_id=tenant_id)
    return memberships


@router.get("/payment-status/{payment_status}", response_model=List[schemas.Membership])
async def read_memberships_by_payment_status(
    payment_status: str,
    current_user: User = Depends(get_current_user)
):
    # Only authorized users can view memberships by payment status
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only authorized users can view memberships by payment status"
        )
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    memberships = await crud.membership.get_memberships_by_payment_status(payment_status=payment_status, tenant_id=tenant_id)
    return memberships


# New endpoints for membership history and statistics
@router.get("/client/{client_id}/history", response_model=List[schemas.Membership])
async def read_membership_history(
    client_id: int,
    current_user: User = Depends(get_current_user)
):
    # Only authorized users can view client membership history
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this client's membership history"
        )

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    # Verify client exists
    client = await crud.client.get_client(client_id=client_id, tenant_id=tenant_id)
    if not client:
         raise HTTPException(status_code=404, detail="Client not found")

    # Get all memberships for the client (past and present)
    memberships = await crud.membership.get_memberships_by_client(client_id=client_id, tenant_id=tenant_id)
    return memberships


# New endpoints for membership types
@router.get("/types", response_model=List[schemas.MembershipType])
async def read_membership_types(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
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

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    return await crud.membership.get_membership_types(skip=skip, limit=limit, active_only=active_only, tenant_id=tenant_id)


@router.post("/types", response_model=schemas.MembershipType)
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

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    return await crud.membership.create_membership_type(
        membership_type.dict(),
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )


@router.get("/types/{membership_type_id}", response_model=schemas.MembershipType)
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

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    db_membership_type = await crud.membership.get_membership_type(membership_type_id=membership_type_id, tenant_id=tenant_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return db_membership_type


@router.put("/types/{membership_type_id}", response_model=schemas.MembershipType)
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

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    db_membership_type = await crud.membership.get_membership_type(membership_type_id=membership_type_id, tenant_id=tenant_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return await crud.membership.update_membership_type(
        membership_type_id=membership_type_id,
        membership_type_update=membership_type_update.dict(exclude_unset=True),
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )


@router.delete("/types/{membership_type_id}", response_model=schemas.MembershipType)
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

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    db_membership_type = await crud.membership.get_membership_type(membership_type_id=membership_type_id, tenant_id=tenant_id)
    if db_membership_type is None:
        raise HTTPException(status_code=404, detail="Membership type not found")

    return await crud.membership.delete_membership_type(
        membership_type_id=membership_type_id,
        user_id=current_user.id,
        ip_address=None,
        user_agent=None,
        tenant_id=tenant_id,
    )


# Enhanced membership endpoints
@router.post("/{membership_id}/use-access", response_model=schemas.Membership)
async def use_membership_access(
    membership_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Increment the access counter for punch-based memberships.
    Only authorized users can log access usage.
    """
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to log access usage"
        )

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    db_membership = await crud.membership.get_membership(membership_id=membership_id, tenant_id=tenant_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Check if it's a punch-based membership
    if not db_membership.membership_type_id or db_membership.accesses_used is None:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is only for punch-based memberships"
        )

    # Check if access limit has been reached
    membership_type = await crud.membership.get_membership_type(db_membership.membership_type_id, tenant_id=tenant_id)
    if membership_type and db_membership.accesses_used >= membership_type.accesses_allowed:
        raise HTTPException(
            status_code=400,
            detail="Access limit already reached for this membership"
        )

    return await crud.membership.increment_access_count(membership_id=membership_id)


@router.get("/{membership_id}/access-usage", response_model=schemas.PunchUsage)
async def get_membership_access_usage(
    membership_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get access usage statistics for a membership.
    Only authorized users can view access usage.
    """
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view access usage"
        )

    usage = await crud.membership.get_punch_usage(membership_id=membership_id)
    if usage is None:
        raise HTTPException(status_code=404, detail="Membership or membership type not found")

    return usage


@router.get("/validate-access/{client_id}", response_model=dict)
async def validate_client_access(
    client_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Validate if a client has valid access rights.
    Only authorized users can validate access.
    """
    if current_user.role not in ["admin", "manager", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to validate access"
        )

    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    return await crud.membership.validate_membership_access(client_id=client_id, tenant_id=tenant_id)
