from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from app.models.tenant import Tenant
from app.models.billing import Plan, Subscription
from app.schemas.billing import PlanResponse, SubscriptionResponse, SubscriptionAssignRequest
from app.utils.tenant import require_super_admin
from app.services.audit_service import AuditService
from app.models.audit_log import ActionTypeEnum

router = APIRouter()


@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(current_user=Depends(require_super_admin)):
    plans = await Plan.filter(status="active").order_by("monthly_price")
    if not plans:
        from app.seeders.seed_plans import seed_plans
        await seed_plans()
        plans = await Plan.filter(status="active").order_by("monthly_price")
    return plans


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def list_subscriptions(current_user=Depends(require_super_admin)):
    subscriptions = await Subscription.all().prefetch_related("tenant", "plan").order_by("-updated_at")
    return [
        {**subscription.__dict__, "tenant_name": subscription.tenant.name, "plan_name": subscription.plan.name}
        for subscription in subscriptions
    ]


@router.get("/tenants/{tenant_id}/subscription", response_model=SubscriptionResponse)
async def get_tenant_subscription(tenant_id: int, current_user=Depends(require_super_admin)):
    subscription = await Subscription.filter(tenant_id=tenant_id).prefetch_related("plan").first()
    if not subscription:
        raise HTTPException(status_code=404, detail="El tenant no tiene suscripción")
    return subscription


@router.put("/tenants/{tenant_id}/subscription", response_model=SubscriptionResponse)
async def assign_tenant_subscription(tenant_id: int, payload: SubscriptionAssignRequest, current_user=Depends(require_super_admin)):
    if not await Tenant.exists(id=tenant_id):
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    plan = await Plan.get_or_none(id=payload.plan_id, status="active")
    if not plan:
        raise HTTPException(status_code=404, detail="Plan activo no encontrado")

    current = await Subscription.filter(tenant_id=tenant_id, status__in=["trialing", "active", "past_due"]).first()
    now = datetime.utcnow()
    if current:
        previous_plan_id = current.plan_id
        current.plan_id = plan.id
        current.status = "active"
        current.renews_at = now + timedelta(days=30)
        await current.save()
        await AuditService.log_action(ActionTypeEnum.UPDATE, current_user.id, "subscription", current.id, {"tenant_id": tenant_id, "plan_id": previous_plan_id}, {"tenant_id": tenant_id, "plan_id": plan.id, "status": current.status}, tenant_id=tenant_id)
        return current

    subscription = await Subscription.create(
        tenant_id=tenant_id,
        plan_id=plan.id,
        status="trialing",
        trial_ends_at=now + timedelta(days=plan.trial_days),
        renews_at=now + timedelta(days=plan.trial_days),
    )
    await AuditService.log_action(ActionTypeEnum.CREATE, current_user.id, "subscription", subscription.id, new_values={"tenant_id": tenant_id, "plan_id": plan.id, "status": subscription.status}, tenant_id=tenant_id)
    return subscription


@router.get("/tenants/{tenant_id}/usage")
async def get_tenant_usage(tenant_id: int, current_user=Depends(require_super_admin)):
    tenant = await Tenant.get_or_none(id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    subscription = await Subscription.filter(tenant_id=tenant_id).prefetch_related("plan").first()
    from app.models.user import User
    from app.models.client import Client
    users = await User.filter(tenant_id=tenant_id).count()
    clients = await Client.filter(tenant_id=tenant_id).count()
    plan = subscription.plan if subscription else None
    return {
        "tenant_id": tenant_id,
        "users": {"used": users, "limit": plan.max_users if plan else tenant.max_users},
        "clients": {"used": clients, "limit": plan.max_clients if plan else None},
        "subscription_status": subscription.status if subscription else None,
        "plan_code": plan.code if plan else None,
    }


@router.post("/tenants/{tenant_id}/subscription/cancel", response_model=SubscriptionResponse)
async def cancel_tenant_subscription(tenant_id: int, current_user=Depends(require_super_admin)):
    subscription = await Subscription.filter(tenant_id=tenant_id, status__in=["trialing", "active", "past_due"]).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No existe una suscripción vigente")
    previous_status = subscription.status
    subscription.status = "canceled"
    subscription.canceled_at = datetime.utcnow()
    await subscription.save()
    await AuditService.log_action(ActionTypeEnum.UPDATE, current_user.id, "subscription", subscription.id, {"status": previous_status}, {"status": subscription.status, "tenant_id": tenant_id}, tenant_id=tenant_id)
    return subscription


@router.post("/tenants/{tenant_id}/subscription/reactivate", response_model=SubscriptionResponse)
async def reactivate_tenant_subscription(tenant_id: int, current_user=Depends(require_super_admin)):
    subscription = await Subscription.filter(tenant_id=tenant_id, status="canceled").first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No existe una suscripción cancelada")
    previous_status = subscription.status
    subscription.status = "active"
    subscription.canceled_at = None
    subscription.renews_at = datetime.utcnow() + timedelta(days=30)
    await subscription.save()
    await AuditService.log_action(ActionTypeEnum.UPDATE, current_user.id, "subscription", subscription.id, {"status": previous_status}, {"status": subscription.status, "tenant_id": tenant_id}, tenant_id=tenant_id)
    return subscription
