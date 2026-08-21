from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.models.billing import Plan, Subscription
from app.schemas.billing import PlanResponse, SubscriptionResponse
from app.utils.tenant import require_super_admin

router = APIRouter()


@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(current_user=Depends(require_super_admin)):
    return await Plan.filter(status="active").order_by("monthly_price")


@router.get("/tenants/{tenant_id}/subscription", response_model=SubscriptionResponse)
async def get_tenant_subscription(tenant_id: int, current_user=Depends(require_super_admin)):
    subscription = await Subscription.filter(tenant_id=tenant_id).prefetch_related("plan").first()
    if not subscription:
        raise HTTPException(status_code=404, detail="El tenant no tiene suscripción")
    return subscription
