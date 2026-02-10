from typing import List, Optional
from datetime import datetime, timedelta
from app.models.membership import Membership, MembershipType
from app.models.client import Client
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q



# CRUD operations for MembershipType
async def get_membership_type(membership_type_id: int) -> Optional[MembershipType]:
    """Get a specific membership type by ID"""
    try:
        return await MembershipType.get(id=membership_type_id)
    except DoesNotExist:
        return None


async def get_membership_types(skip: int = 0, limit: int = 100, active_only: bool = False) -> List[MembershipType]:
    """Get all membership types with optional filtering"""
    query = MembershipType.all()
    if active_only:
        query = query.filter(is_active=True)
    return await query.offset(skip).limit(limit)


async def create_membership_type(membership_type_data: dict) -> MembershipType:
    """Create a new membership type"""
    return await MembershipType.create(**membership_type_data)


async def update_membership_type(membership_type_id: int, membership_type_update: dict) -> Optional[MembershipType]:
    """Update a membership type"""
    membership_type = await get_membership_type(membership_type_id)
    if membership_type:
        for field, value in membership_type_update.items():
            setattr(membership_type, field, value)
        await membership_type.save()
    return membership_type


async def delete_membership_type(membership_type_id: int) -> Optional[MembershipType]:
    """Deactivate a membership type (soft delete)"""
    membership_type = await get_membership_type(membership_type_id)
    if membership_type:
        membership_type.is_active = False
        await membership_type.save()
    return membership_type


# Enhanced CRUD operations for Membership with new features
async def get_membership(membership_id: int) -> Optional[Membership]:
    """Get a specific membership by ID"""
    try:
        return await Membership.get(id=membership_id)
    except DoesNotExist:
        return None


async def get_memberships(skip: int = 0, limit: int = 100) -> List[Membership]:
    """Get all memberships with pagination"""
    return await Membership.all().offset(skip).limit(limit)


async def get_memberships_by_client(client_id: int) -> List[Membership]:
    """Get all memberships for a specific client"""
    return await Membership.filter(client_id=client_id)


async def get_active_membership(client_id: int) -> Optional[Membership]:
    """Get the currently active membership for a client"""
    return await Membership.filter(
        client_id=client_id,
        status="active",
        end_date__gte=datetime.utcnow()
    ).order_by("-end_date").first()


async def create_membership(membership_data: dict) -> Membership:
    """Create a new membership with automatic date calculation based on membership type"""
    # If membership_type_id is provided, get the type to calculate dates
    membership_type = None
    if membership_data.get('membership_type_id'):
        membership_type = await get_membership_type(membership_data['membership_type_id'])
    
    # Calculate end_date if not provided and membership type exists
    start_date = membership_data.get('start_date') or datetime.utcnow()
    end_date = membership_data.get('end_date')
    
    if membership_type and not end_date:
        if membership_type.duration_days:
            end_date = start_date + timedelta(days=membership_type.duration_days)
        else:
            # Default to 30 days if no duration specified
            end_date = start_date + timedelta(days=30)
    
    # Set price_paid to membership_type.price if not provided
    price_paid = membership_data.get('price_paid') or (membership_type.price if membership_type else membership_data['price'])
    
    membership_data['start_date'] = start_date
    membership_data['end_date'] = end_date
    membership_data['price_paid'] = price_paid
    membership_data['type'] = membership_data.get('type') or (membership_type.name if membership_type else "General")
    
    return await Membership.create(**membership_data)


async def update_membership(membership_id: int, membership_update: dict) -> Optional[Membership]:
    """Update a membership"""
    membership = await get_membership(membership_id)
    if membership:
        for field, value in membership_update.items():
            setattr(membership, field, value)
        await membership.save()
    return membership


async def delete_membership(membership_id: int) -> Optional[Membership]:
    """Delete a membership"""
    membership = await get_membership(membership_id)
    if membership:
        await membership.delete()
    return membership


async def get_expired_memberships() -> List[Membership]:
    """Get all expired memberships"""
    return await Membership.filter(
        Q(status="expired") | Q(end_date__lt=datetime.utcnow())
    )


async def get_memberships_by_status(status: str) -> List[Membership]:
    """Get all memberships with a specific status"""
    return await Membership.filter(status=status)


async def get_memberships_by_payment_status(payment_status: str) -> List[Membership]:
    """Get all memberships with a specific payment status"""
    return await Membership.filter(payment_status=payment_status)


async def get_total_memberships_count() -> int:
    """Get the total count of all memberships"""
    return await Membership.all().count()


async def get_active_memberships_count() -> int:
    """Get the count of active memberships"""
    return await Membership.filter(
        status="active",
        end_date__gte=datetime.utcnow()
    ).count()


async def get_expired_memberships_count() -> int:
    """Get the count of expired memberships"""
    return await Membership.filter(
        Q(status="expired") | Q(end_date__lt=datetime.utcnow())
    ).count()


async def get_upcoming_expirations(days: int = 30) -> List[Membership]:
    """Get memberships that will expire within the specified number of days"""
    future_date = datetime.utcnow() + timedelta(days=days)
    return await Membership.filter(
        status="active",
        end_date__gte=datetime.utcnow(),
        end_date__lte=future_date
    ).order_by("end_date")


async def increment_access_count(membership_id: int) -> Optional[Membership]:
    """Increment the access counter for punch-based memberships"""
    membership = await get_membership(membership_id)
    if membership:
        membership.accesses_used += 1
        await membership.save()
    return membership


async def get_punch_usage(membership_id: int) -> Optional[dict]:
    """Get access usage statistics for a membership"""
    membership = await get_membership(membership_id)
    if not membership or not membership.membership_type_id:
        return None
    
    membership_type = await get_membership_type(membership.membership_type_id)
    if not membership_type:
        return None
        
    total_accesses = membership_type.accesses_allowed
    accesses_used = membership.accesses_used
    accesses_remaining = None if total_accesses is None else max(0, total_accesses - accesses_used)
    
    return {
        "total_accesses_allowed": total_accesses,
        "accesses_used": accesses_used,
        "accesses_remaining": accesses_remaining
    }


async def validate_membership_access(client_id: int) -> dict:
    """Validate if a client has valid access rights"""
    # Get the currently active membership for the client
    active_membership = await get_active_membership(client_id)
    
    if not active_membership:
        return {
            "valid_access": False,
            "message": "No active membership found"
        }
    
    # Check if it's a punch-based membership and if accesses are available
    if active_membership.membership_type_id:
        membership_type = await get_membership_type(active_membership.membership_type_id)
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
        membership_type = await get_membership_type(active_membership.membership_type_id)
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