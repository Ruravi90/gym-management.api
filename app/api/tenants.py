from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import re
import unicodedata
import re
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantStats
from app.crud import tenant as tenant_crud
from app.utils.tenant import require_super_admin
from app.models.user import User as UserModel
from app.config import settings
from app.services.waha import send_text, send_text_result, delete_session, tenant_session_name

router = APIRouter()

@router.get("/waha/status")
async def waha_status(current_user: UserModel = Depends(require_super_admin)):
    """Estado seguro de la sesión master; nunca expone la API key."""
    configured = bool(settings.WAHA_BASE_URL and settings.WAHA_MASTER_SESSION)
    return {
        "configured": configured,
        "active": configured,
        "session": settings.WAHA_MASTER_SESSION if configured else None,
        "base_url": settings.WAHA_BASE_URL if configured else None,
    }

@router.post("/waha/test-message")
async def waha_test_message(payload: dict, current_user: UserModel = Depends(require_super_admin)):
    phone = str(payload.get("phone", "")).strip()
    message = str(payload.get("message", "")).strip()
    if not re.fullmatch(r"[0-9]{10}", phone):
        raise HTTPException(status_code=400, detail="El teléfono debe contener exactamente 10 dígitos de México")
    if not message or len(message) > 500:
        raise HTTPException(status_code=400, detail="El mensaje es obligatorio y debe tener máximo 500 caracteres")
    if not settings.WAHA_ENABLED:
        raise HTTPException(status_code=503, detail="WAHA está deshabilitado en la configuración")
    sent, detail = await send_text_result(f"+52{phone}", message, settings.WAHA_MASTER_SESSION)
    if not sent:
        raise HTTPException(status_code=502, detail=detail or "WAHA no aceptó el envío del mensaje")
    return {"message": "Mensaje enviado correctamente", "phone": f"+52{phone}"}


@router.delete("/{tenant_id}/waha-session")
async def delete_tenant_waha_session(tenant_id: int, current_user: UserModel = Depends(require_super_admin)):
    """Elimina una sesión propia de tenant; la sesión master nunca se elimina aquí."""
    tenant = await tenant_crud.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return await delete_session(tenant_session_name(tenant_id))


def _slug_base(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return (slug or "gimnasio")[:50].rstrip("-")


async def _unique_slug(name: str) -> str:
    base = _slug_base(name)
    candidate = base
    suffix = 2
    while await tenant_crud.get_tenant_by_slug(candidate):
        suffix_text = f"-{suffix}"
        candidate = f"{base[:50 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return candidate


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
    data = tenant_in.model_dump()
    data["slug"] = await _unique_slug(tenant_in.name)
    return await tenant_crud.create_tenant(data)


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
