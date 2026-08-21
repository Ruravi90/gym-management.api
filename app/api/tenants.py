from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantStats
from app.crud import tenant as tenant_crud
from app.utils.tenant import require_super_admin
from app.models.user import User as UserModel

router = APIRouter()


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    tenant_status: Optional[str] = Query(None, alias="status"),
    current_user: UserModel = Depends(require_super_admin),
):
    return await tenant_crud.get_tenants(skip=skip, limit=limit, status=tenant_status)


@router.get("/count")
async def count_tenants(current_user: UserModel = Depends(require_super_admin)):
    total = await tenant_crud.count_tenants()
    active = await tenant_crud.count_tenants(status="active")
    return {"total": total, "active": active}


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    current_user: UserModel = Depends(require_super_admin),
):
    existing = await tenant_crud.get_tenant_by_slug(tenant_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="El slug ya está en uso")
    return await tenant_crud.create_tenant(tenant_in.model_dump())


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    current_user: UserModel = Depends(require_super_admin),
):
    tenant = await tenant_crud.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_in: TenantUpdate,
    current_user: UserModel = Depends(require_super_admin),
):
    tenant = await tenant_crud.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    update_data = tenant_in.model_dump(exclude_unset=True)
    return await tenant_crud.update_tenant(tenant_id, update_data)


@router.delete("/{tenant_id}", response_model=TenantResponse)
async def delete_tenant(
    tenant_id: int,
    current_user: UserModel = Depends(require_super_admin),
):
    tenant = await tenant_crud.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    await tenant_crud.delete_tenant(tenant_id)
    return tenant


@router.get("/{tenant_id}/stats", response_model=TenantStats)
async def get_tenant_stats(
    tenant_id: int,
    current_user: UserModel = Depends(require_super_admin),
):
    stats = await tenant_crud.get_tenant_stats(tenant_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return stats


@router.post("/{tenant_id}/assign-admin")
async def assign_admin_to_tenant(
    tenant_id: int,
    payload: dict,
    current_user: UserModel = Depends(require_super_admin),
):
    from app.crud.user import get_user, update_user

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id es obligatorio")

    tenant = await tenant_crud.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await update_user(user_id, {"tenant_id": tenant_id, "role": "admin"})
    return {"message": f"Usuario {user_id} asignado como admin del tenant {tenant_id}"}
