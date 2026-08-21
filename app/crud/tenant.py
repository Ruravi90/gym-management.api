from typing import List, Optional
from app.models.tenant import Tenant, TenantStatus
from tortoise.exceptions import DoesNotExist


async def get_tenant(tenant_id: int) -> Optional[Tenant]:
    try:
        return await Tenant.get(id=tenant_id)
    except DoesNotExist:
        return None


async def get_tenant_by_slug(slug: str) -> Optional[Tenant]:
    try:
        return await Tenant.get(slug=slug)
    except DoesNotExist:
        return None


async def get_tenants(skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Tenant]:
    query = Tenant.all()
    if status:
        query = query.filter(status=status)
    return await query.order_by("-created_at").offset(skip).limit(limit)


async def count_tenants(status: Optional[str] = None) -> int:
    if status:
        return await Tenant.filter(status=status).count()
    return await Tenant.all().count()


async def create_tenant(data: dict) -> Tenant:
    return await Tenant.create(**data)


async def update_tenant(tenant_id: int, update_data: dict) -> Optional[Tenant]:
    tenant = await get_tenant(tenant_id)
    if not tenant:
        return None
    for field, value in update_data.items():
        if value is not None:
            setattr(tenant, field, value)
    await tenant.save()
    return tenant


async def delete_tenant(tenant_id: int) -> Optional[Tenant]:
    tenant = await get_tenant(tenant_id)
    if tenant:
        await tenant.delete()
    return tenant


async def get_tenant_stats(tenant_id: int) -> dict:
    from app.models.user import User
    from app.models.client import Client
    from app.models.membership import Membership

    tenant = await get_tenant(tenant_id)
    if not tenant:
        return None

    total_users = await User.filter(tenant_id=tenant_id).count()
    total_clients = await Client.filter(tenant_id=tenant_id).count()
    active_memberships = await Membership.filter(
        tenant_id=tenant_id, status="active"
    ).count()

    # Revenue from active memberships
    memberships = await Membership.filter(
        tenant_id=tenant_id, payment_status="paid"
    ).all()
    total_revenue = sum(m.price_paid or m.price for m in memberships)

    return {
        "tenant_id": tenant_id,
        "tenant_name": tenant.name,
        "total_users": total_users,
        "total_clients": total_clients,
        "active_memberships": active_memberships,
        "total_revenue": total_revenue,
    }
