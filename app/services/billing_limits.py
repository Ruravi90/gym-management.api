from fastapi import HTTPException, status
from app.models.billing import Subscription
from app.models.client import Client
from app.models.tenant import Tenant
from app.models.user import User


async def ensure_within_limit(tenant_id: int | None, resource: str) -> None:
    """Validate a tenant limit without affecting super-admin platform operations."""
    if tenant_id is None:
        return
    subscription = await Subscription.filter(tenant_id=tenant_id, status__in=["trialing", "active"]).prefetch_related("plan").first()
    if not subscription:
        return
    used = await (User.filter(tenant_id=tenant_id).count() if resource == "users" else Client.filter(tenant_id=tenant_id).count())
    limit = subscription.plan.max_users if resource == "users" else subscription.plan.max_clients
    if used >= limit:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Límite de {resource} alcanzado para el plan {subscription.plan.name}")
