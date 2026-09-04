from fastapi import APIRouter, Depends, HTTPException, Response
from app.models.user import User as UserModel
from app.utils.tenant import require_tenant_user
from app.services import waha

router = APIRouter()


def tenant_id(user: UserModel) -> int:
    if not user.tenant_id:
        raise HTTPException(status_code=403, detail="Usuario no asignado a un tenant")
    return user.tenant_id


def session_for(user: UserModel) -> str:
    # El tenant operativo del Super Admin usa la sesión master del sistema.
    if user.role == "super_admin":
        return waha.settings.WAHA_MASTER_SESSION
    return waha.tenant_session_name(tenant_id(user))


@router.get("")
async def status(current_user: UserModel = Depends(require_tenant_user)):
    try:
        return await waha.get_session_status(session_for(current_user))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/connect")
async def connect(current_user: UserModel = Depends(require_tenant_user)):
    try:
        if current_user.role == "super_admin":
            return await waha.get_session_status(session_for(current_user))
        return await waha.create_or_start_tenant_session(tenant_id(current_user))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/qr")
async def qr(current_user: UserModel = Depends(require_tenant_user)):
    try:
        response = await waha.get_session_qr(session_for(current_user))
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="La sesión del tenant no existe")
        response.raise_for_status()
        return Response(content=response.content, media_type=response.headers.get("content-type", "image/png"))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/disconnect")
async def disconnect(current_user: UserModel = Depends(require_tenant_user)):
    try:
        return await waha.logout_session(session_for(current_user))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
