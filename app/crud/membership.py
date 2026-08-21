from typing import List, Optional
from datetime import datetime, timedelta, timezone
from app.models.membership import Membership, MembershipType
from app.models.client import Client
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from app.services.audit_service import AuditService
from app.models.audit_log import ActionTypeEnum


# CRUD operations for MembershipType
async def get_membership_type(membership_type_id: int, tenant_id: Optional[int] = None) -> Optional[MembershipType]:
    try:
        filters = {"id": membership_type_id}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await MembershipType.get(**filters)
    except DoesNotExist:
        return None


async def get_membership_types(skip: int = 0, limit: int = 100, active_only: bool = False, tenant_id: Optional[int] = None) -> List[MembershipType]:
    query = MembershipType.all()
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    if active_only:
        query = query.filter(is_active=True)
    return await query.offset(skip).limit(limit)


async def create_membership_type(
    membership_type_data: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> MembershipType:
    if tenant_id is not None:
        membership_type_data["tenant_id"] = tenant_id
    membership_type = await MembershipType.create(**membership_type_data)

    await AuditService.log_creation(
        user_id=user_id,
        entity_type="MembershipType",
        entity_id=membership_type.id,
        new_values=await AuditService.extract_entity_values_for_audit(membership_type),
        ip_address=ip_address,
        user_agent=user_agent,
        tenant_id=tenant_id,
    )

    return membership_type


async def update_membership_type(
    membership_type_id: int,
    membership_type_update: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[MembershipType]:
    membership_type = await get_membership_type(membership_type_id, tenant_id=tenant_id)
    if membership_type:
        old_values = await AuditService.extract_entity_values_for_audit(membership_type)

        for field, value in membership_type_update.items():
            setattr(membership_type, field, value)
        await membership_type.save()

        new_values = await AuditService.extract_entity_values_for_audit(membership_type)

        await AuditService.log_update(
            user_id=user_id,
            entity_type="MembershipType",
            entity_id=membership_type.id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )

    return membership_type


async def delete_membership_type(
    membership_type_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[MembershipType]:
    membership_type = await get_membership_type(membership_type_id, tenant_id=tenant_id)
    if membership_type:
        old_values = await AuditService.extract_entity_values_for_audit(membership_type)

        membership_type.is_active = False
        await membership_type.save()

        new_values = await AuditService.extract_entity_values_for_audit(membership_type)

        await AuditService.log_update(
            user_id=user_id,
            entity_type="MembershipType",
            entity_id=membership_type.id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )
    return membership_type


# Enhanced CRUD operations for Membership with new features
async def get_membership(membership_id: int, tenant_id: Optional[int] = None) -> Optional[Membership]:
    try:
        filters = {"id": membership_id}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await Membership.get(**filters)
    except DoesNotExist:
        return None


async def get_memberships(skip: int = 0, limit: int = 100, tenant_id: Optional[int] = None) -> List[Membership]:
    query = Membership.all()
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.offset(skip).limit(limit)


async def get_memberships_by_client(client_id: int, tenant_id: Optional[int] = None) -> List[Membership]:
    filters = {"client_id": client_id}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Membership.filter(**filters)


async def get_active_membership(client_id: int, tenant_id: Optional[int] = None) -> Optional[Membership]:
    filters = {
        "client_id": client_id,
        "status": "active",
        "end_date__gte": datetime.now(timezone.utc),
    }
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Membership.filter(**filters).order_by("-end_date").first()


async def create_membership(
    membership_data: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Membership:
    membership_type = None
    if membership_data.get('membership_type_id'):
        membership_type = await get_membership_type(membership_data['membership_type_id'], tenant_id=tenant_id)

    start_date = membership_data.get('start_date') or datetime.now(timezone.utc)
    end_date = membership_data.get('end_date')

    if membership_type and not end_date:
        if membership_type.duration_days:
            end_date = start_date + timedelta(days=membership_type.duration_days)
        else:
            end_date = start_date + timedelta(days=30)

    base_price = membership_data.get('price')
    if base_price is None and membership_type:
        base_price = membership_type.price
    elif base_price is None:
        base_price = 0.0

    price_paid = membership_data.get('price_paid')
    if price_paid is None:
        price_paid = base_price

    membership_data['start_date'] = start_date
    membership_data['end_date'] = end_date
    membership_data['price'] = base_price
    membership_data['price_paid'] = price_paid
    membership_data['type'] = membership_data.get('type') or (membership_type.name if membership_type else "General")

    if tenant_id is not None:
        membership_data['tenant_id'] = tenant_id

    membership = await Membership.create(**membership_data)

    await AuditService.log_creation(
        user_id=user_id,
        entity_type="Membership",
        entity_id=membership.id,
        new_values=await AuditService.extract_entity_values_for_audit(membership),
        ip_address=ip_address,
        user_agent=user_agent,
        tenant_id=tenant_id,
    )

    return membership


async def update_membership(
    membership_id: int,
    membership_update: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[Membership]:
    membership = await get_membership(membership_id, tenant_id=tenant_id)
    if membership:
        old_values = await AuditService.extract_entity_values_for_audit(membership)

        for field, value in membership_update.items():
            setattr(membership, field, value)
        await membership.save()

        new_values = await AuditService.extract_entity_values_for_audit(membership)

        await AuditService.log_update(
            user_id=user_id,
            entity_type="Membership",
            entity_id=membership.id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )

    return membership


async def delete_membership(
    membership_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[Membership]:
    membership = await get_membership(membership_id, tenant_id=tenant_id)
    if membership:
        old_values = await AuditService.extract_entity_values_for_audit(membership)

        await membership.delete()

        await AuditService.log_deletion(
            user_id=user_id,
            entity_type="Membership",
            entity_id=membership.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )
    return membership


async def get_expired_memberships(tenant_id: Optional[int] = None) -> List[Membership]:
    query = Membership.filter(
        Q(status="expired") | Q(end_date__lt=datetime.now(timezone.utc))
    )
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query


async def get_memberships_by_status(status: str, tenant_id: Optional[int] = None) -> List[Membership]:
    filters = {"status": status}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Membership.filter(**filters)


async def get_memberships_by_payment_status(payment_status: str, tenant_id: Optional[int] = None) -> List[Membership]:
    filters = {"payment_status": payment_status}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Membership.filter(**filters)


async def get_total_memberships_count(tenant_id: Optional[int] = None) -> int:
    query = Membership.all()
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.count()


async def get_active_memberships_count(tenant_id: Optional[int] = None) -> int:
    filters = {
        "status": "active",
        "end_date__gte": datetime.now(timezone.utc),
    }
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Membership.filter(**filters).count()


async def get_expired_memberships_count(tenant_id: Optional[int] = None) -> int:
    query = Membership.filter(
        Q(status="expired") | Q(end_date__lt=datetime.now(timezone.utc))
    )
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.count()


async def get_upcoming_expirations(days: int = 30, tenant_id: Optional[int] = None) -> List[Membership]:
    future_date = datetime.now(timezone.utc) + timedelta(days=days)
    filters = {
        "status": "active",
        "end_date__gte": datetime.now(timezone.utc),
        "end_date__lte": future_date,
    }
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Membership.filter(**filters).order_by("end_date")


async def increment_access_count(membership_id: int) -> Optional[Membership]:
    membership = await get_membership(membership_id)
    if membership:
        membership.accesses_used += 1
        await membership.save()
    return membership


async def get_punch_usage(membership_id: int) -> Optional[dict]:
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


async def validate_membership_access(client_id: int, tenant_id: Optional[int] = None) -> dict:
    active_membership = await get_active_membership(client_id, tenant_id=tenant_id)

    if not active_membership:
        return {
            "valid_access": False,
            "message": "No active membership found"
        }

    if active_membership.membership_type_id:
        membership_type = await get_membership_type(active_membership.membership_type_id, tenant_id=tenant_id)
        if membership_type and membership_type.accesses_allowed is not None:
            if active_membership.accesses_used >= membership_type.accesses_allowed:
                return {
                    "valid_access": False,
                    "message": "Access limit exceeded for punch-based membership"
                }

    if active_membership.end_date < datetime.now(timezone.utc):
        return {
            "valid_access": False,
            "message": "Membership has expired"
        }

    total_accesses = None
    accesses_remaining = None
    if active_membership.membership_type_id:
        membership_type = await get_membership_type(active_membership.membership_type_id, tenant_id=tenant_id)
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
