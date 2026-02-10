from typing import List
from fastapi import HTTPException
from app.models.membership import Membership, MembershipType
from app.models.client import Client
from app.crud import membership as crud_membership
from app.schemas import membership as schemas
from app.utils.auth import get_current_user
from app.models.user import User
from fastapi import Depends
from tortoise.exceptions import DoesNotExist


async def get_membership(membership_id: int) -> schemas.Membership:
    """Get a specific membership by ID"""
    try:
        membership = await Membership.get(id=membership_id)
        return schemas.Membership.from_orm(membership)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Membership not found")


async def get_memberships(skip: int = 0, limit: int = 100) -> List[schemas.Membership]:
    """Get all memberships with pagination"""
    memberships = await Membership.all().offset(skip).limit(limit)
    return [schemas.Membership.from_orm(m) for m in memberships]


async def create_membership(membership_data: schemas.MembershipCreate) -> schemas.Membership:
    """Create a new membership"""
    membership = await Membership.create(**membership_data.dict())
    return schemas.Membership.from_orm(membership)


async def update_membership(membership_id: int, membership_update: schemas.MembershipUpdate) -> schemas.Membership:
    """Update a membership"""
    membership = await get_membership(membership_id)
    update_data = membership_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(membership, field, value)
    await membership.save()
    return schemas.Membership.from_orm(membership)


async def delete_membership(membership_id: int) -> schemas.Membership:
    """Delete a membership"""
    membership = await get_membership(membership_id)
    await membership.delete()
    return schemas.Membership.from_orm(membership)


async def get_memberships_by_client(client_id: int) -> List[schemas.Membership]:
    """Get all memberships for a specific client"""
    memberships = await Membership.filter(client_id=client_id)
    return [schemas.Membership.from_orm(m) for m in memberships]


async def get_active_membership(client_id: int) -> schemas.Membership:
    """Get the currently active membership for a client"""
    from datetime import datetime
    membership = await Membership.filter(
        client_id=client_id,
        status="active",
        end_date__gte=datetime.utcnow()
    ).order_by("-end_date").first()
    if not membership:
        raise HTTPException(status_code=404, detail="Active membership not found")
    return schemas.Membership.from_orm(membership)


async def get_memberships_by_status(status: str) -> List[schemas.Membership]:
    """Get all memberships with a specific status"""
    memberships = await Membership.filter(status=status)
    return [schemas.Membership.from_orm(m) for m in memberships]


async def get_memberships_by_payment_status(payment_status: str) -> List[schemas.Membership]:
    """Get all memberships with a specific payment status"""
    memberships = await Membership.filter(payment_status=payment_status)
    return [schemas.Membership.from_orm(m) for m in memberships]


async def get_total_memberships_count() -> int:
    """Get the total count of all memberships"""
    return await Membership.all().count()


async def get_active_memberships_count() -> int:
    """Get the count of active memberships"""
    from datetime import datetime
    return await Membership.filter(
        status="active",
        end_date__gte=datetime.utcnow()
    ).count()


async def get_expired_memberships_count() -> int:
    """Get the count of expired memberships"""
    from datetime import datetime
    return await Membership.filter(
        status="expired"
    ).or_(end_date__lt=datetime.utcnow()).count()


async def get_upcoming_expirations(days: int = 30) -> List[schemas.Membership]:
    """Get memberships that will expire within the specified number of days"""
    from datetime import datetime, timedelta
    future_date = datetime.utcnow() + timedelta(days=days)
    memberships = await Membership.filter(
        status="active",
        end_date__gte=datetime.utcnow(),
        end_date__lte=future_date
    ).order_by("end_date")
    return [schemas.Membership.from_orm(m) for m in memberships]


# New methods for membership types
async def get_membership_types(skip: int = 0, limit: int = 100, active_only: bool = False) -> List[schemas.MembershipType]:
    """Get all membership types with optional filtering"""
    query = MembershipType.all()
    if active_only:
        query = query.filter(is_active=True)
    membership_types = await query.offset(skip).limit(limit)
    return [schemas.MembershipType.from_orm(mt) for mt in membership_types]


async def get_membership_type(membership_type_id: int) -> schemas.MembershipType:
    """Get a specific membership type by ID"""
    try:
        membership_type = await MembershipType.get(id=membership_type_id)
        return schemas.MembershipType.from_orm(membership_type)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Membership type not found")


async def create_membership_type(membership_type: schemas.MembershipTypeCreate) -> schemas.MembershipType:
    """Create a new membership type"""
    membership_type_obj = await MembershipType.create(**membership_type.dict())
    return schemas.MembershipType.from_orm(membership_type_obj)


async def update_membership_type(membership_type_id: int, membership_type_update: schemas.MembershipTypeUpdate) -> schemas.MembershipType:
    """Update a membership type"""
    membership_type = await get_membership_type(membership_type_id)
    update_data = membership_type_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(membership_type, field, value)
    await membership_type.save()
    return schemas.MembershipType.from_orm(membership_type)


async def delete_membership_type(membership_type_id: int) -> schemas.MembershipType:
    """Deactivate a membership type (soft delete)"""
    membership_type = await get_membership_type(membership_type_id)
    membership_type.is_active = False
    await membership_type.save()
    return schemas.MembershipType.from_orm(membership_type)


# Enhanced membership methods
async def increment_access_count(membership_id: int) -> schemas.Membership:
    """Increment the access counter for punch-based memberships"""
    membership = await get_membership(membership_id)
    membership.accesses_used += 1
    await membership.save()
    return schemas.Membership.from_orm(membership)


async def get_punch_usage(membership_id: int) -> schemas.PunchUsage:
    """Get access usage statistics for a membership"""
    membership = await get_membership(membership_id)
    if not membership or not membership.membership_type_id:
        raise HTTPException(status_code=404, detail="Membership or membership type not found")
    
    membership_type = await get_membership_type(membership.membership_type_id)
    total_accesses = membership_type.accesses_allowed
    accesses_used = membership.accesses_used
    accesses_remaining = None if total_accesses is None else max(0, total_accesses - accesses_used)
    
    return schemas.PunchUsage(
        total_accesses_allowed=total_accesses,
        accesses_used=accesses_used,
        accesses_remaining=accesses_remaining
    )


async def validate_membership_access(client_id: int) -> dict:
    """Validate if a client has valid access rights"""
    from datetime import datetime
    
    # Get the currently active membership for the client
    try:
        active_membership = await Membership.filter(
            client_id=client_id,
            status="active",
            end_date__gte=datetime.utcnow()
        ).order_by("-end_date").first()
        
        if not active_membership:
            return {
                "valid_access": False,
                "message": "No active membership found"
            }
        
        # Check if it's a punch-based membership and if accesses are available
        if active_membership.membership_type_id:
            membership_type = await MembershipType.get(id=active_membership.membership_type_id)
            if membership_type and membership_type.accesses_allowed is not None:
                if active_membership.accesses_used >= membership_type.accesses_allowed:
                    return {
                        "valid_access": False,
                        "message": "Access limit exceeded for punch-based membership"
                    }
        
        # Check if the membership hasn't expired
        if active_membership.end_date < datetime.utcnow():
            return {
                "valid_access": False,
                "message": "Membership has expired"
            }
        
        # Access is valid
        total_accesses = None
        accesses_remaining = None
        if active_membership.membership_type_id:
            membership_type = await MembershipType.get(id=active_membership.membership_type_id)
            if membership_type:
                total_accesses = membership_type.accesses_allowed
                accesses_remaining = None if total_accesses is None else max(0, total_accesses - active_membership.accesses_used)
        
        return {
            "valid_access": True,
            "membership_id": active_membership.id,
            "membership_type": active_membership.type,
            "expires_at": active_membership.end_date,
            "accesses_remaining": accesses_remaining
        }
    except DoesNotExist:
        return {
            "valid_access": False,
            "message": "No active membership found"
        }