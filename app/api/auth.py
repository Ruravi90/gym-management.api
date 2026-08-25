from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, WebSocket, WebSocketDisconnect, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
import logging
from app import crud, schemas
from app.utils.auth import (
    authenticate_user, create_access_token, create_refresh_token,
    verify_refresh_token, get_current_user,
    set_auth_cookies, clear_auth_cookies, REFRESH_TOKEN_COOKIE,
    verify_password_setup_token,
)
from app.config import settings
from app.middleware.security import limiter, auth_limits
from app.services.qr_service import generate_qr_token
from app.services.pin_service import generate_pin
from app.services.checkin_notifier import subscribe_checkin, notify_checkin
from app.models.user import User
from tortoise.transactions import in_transaction
from tortoise.expressions import Q
from secrets import token_urlsafe
import hashlib

logger = logging.getLogger(__name__)


router = APIRouter()

COMMON_PASSWORDS = {"123456", "password", "12345678", "qwerty", "123456789", "111111", "abc123", "123123", "admin123", "contraseña", "password1"}

def validate_new_password(password: object) -> str | None:
    if not isinstance(password, str) or len(password) < 6:
        return "La contraseña debe tener al menos 6 caracteres"
    normalized = password.strip().lower()
    if normalized in COMMON_PASSWORDS:
        return "Elige una contraseña menos común"
    if len(set(normalized)) == 1 or normalized in "0123456789abcdefghijklmnopqrstuvwxyz":
        return "Elige una contraseña menos predecible"
    return None

async def _forgot_password(payload: dict, audience: str):
    identifier = str(payload.get("identifier", "")).strip()
    generic = {"message": "Si la cuenta existe y tiene teléfono, recibirás un enlace por WhatsApp."}
    if not identifier:
        return generic
    user = None
    if audience == "member":
        from app.models.client import Client
        digits = "".join(ch for ch in identifier if ch.isdigit())
        phone_values = [identifier, digits, f"+52{digits}", f"52{digits}"] if len(digits) == 10 else [identifier]
        client_matches = await Client.filter(Q(email=identifier.lower()) | Q(phone__in=phone_values)).filter(status=True).prefetch_related("user")
        users = [client.user for client in client_matches if client.user and client.user.status]
        user = users[0] if len({item.id for item in users}) == 1 else None
    else:
        user = await User.get_or_none(email=identifier.lower())
    if not user and audience == "admin":
        digits = "".join(ch for ch in identifier if ch.isdigit())
        if len(digits) == 10:
            phone_matches = await User.filter(phone__in=[digits, f"+52{digits}", f"52{digits}"]).all()
            # No enviar a una cuenta arbitraria si el teléfono todavía está duplicado.
            candidates = [item for item in phone_matches if item.status and item.role in ("admin", "manager", "receptionist", "super_admin")]
            user = candidates[0] if len(candidates) == 1 else None
    if not user or not user.status or not user.phone or not settings.PORTAL_URL or not settings.PORTAL_URL.startswith(("http://", "https://")):
        return generic
    raw_token = token_urlsafe(32)
    user.password_reset_token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    user.password_reset_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=20)
    await user.save(update_fields=["password_reset_token_hash", "password_reset_expires_at", "updated_at"])
    from app.services.waha import send_text
    link = f"{settings.PORTAL_URL.rstrip('/')}/activar-cuenta?reset={raw_token}"
    await send_text(user.phone, f"Recibimos una solicitud para cambiar tu contraseña de MyGym. Usa este enlace (válido 20 minutos): {link}", settings.WAHA_MASTER_SESSION)
    return generic

@router.post("/member/forgot-password")
async def member_forgot_password(payload: dict):
    return await _forgot_password(payload, "member")

@router.post("/admin/forgot-password")
async def admin_forgot_password(payload: dict):
    return await _forgot_password(payload, "admin")

@router.post("/set-password")
async def set_password(payload: dict):
    password = payload.get("password", "")
    password_error = validate_new_password(password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)
    reset_token = payload.get("reset") or payload.get("reset_token")
    if reset_token:
        token_hash = hashlib.sha256(str(reset_token).encode()).hexdigest()
        async with in_transaction() as connection:
            user = await User.filter(password_reset_token_hash=token_hash).using_db(connection).select_for_update().first()
            if not user or not user.status or not user.password_reset_expires_at or user.password_reset_expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
                raise HTTPException(status_code=410, detail="El enlace de recuperación es inválido o expiró")
            user.hashed_password = __import__("app.utils.auth", fromlist=["hash_password"]).hash_password(password)
            user.password_reset_token_hash = None
            user.password_reset_expires_at = None
            await user.save(using_db=connection, update_fields=["hashed_password", "password_reset_token_hash", "password_reset_expires_at", "updated_at"])
        return {"message": "Contraseña actualizada correctamente"}
    user_id = verify_password_setup_token(payload.get("token", ""))
    if not user_id:
        raise HTTPException(status_code=400, detail="Enlace inválido o contraseña demasiado corta")
    from app.utils.auth import hash_password
    from datetime import datetime, timezone
    async with in_transaction() as connection:
        user = await User.filter(id=user_id).using_db(connection).select_for_update().first()
        if not user or not user.status:
            raise HTTPException(status_code=404, detail="Usuario no encontrado o inactivo")
        if user.password_setup_at is not None:
            raise HTTPException(status_code=410, detail="Este enlace de activación ya fue utilizado")
        user.hashed_password = hash_password(password)
        user.password_setup_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await user.save(using_db=connection, update_fields=["hashed_password", "password_setup_at", "updated_at"])
    return {"message": "Contraseña configurada correctamente"}

@router.post("/login")
@limiter.limit(auth_limits)
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible login, sets HttpOnly cookies for access and refresh tokens.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    set_auth_cookies(response, access_token, refresh_token, request)

    return {"message": "Login successful"}


@router.post("/refresh")
@limiter.limit(auth_limits)
async def refresh_token(request: Request, response: Response):
    """
    Rotate tokens using the refresh_token cookie. Sets new HttpOnly cookies.
    """
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_refresh_token(refresh_token_value)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await User.get_or_none(id=int(user_id))
    except Exception:
        user = None

    if not user or not user.status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    set_auth_cookies(response, new_access_token, new_refresh_token, request)

    return {"message": "Token refreshed"}


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Clear auth cookies."""
    clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.post("/register", response_model=schemas.User)
@limiter.limit(auth_limits)
async def register(request: Request, user_data: schemas.UserRegister):
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = await crud.user.get_user_by_email(email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with hashed password
    user_dict = {
        "email": user_data.email,
        "name": user_data.name,
        "phone": user_data.phone,
        "password": user_data.password
    }

    # Assign to the default tenant if tenant_id is provided
    tenant_id = getattr(user_data, 'tenant_id', None)

    user = await crud.user.create_user(user_data=user_dict, tenant_id=tenant_id)

    # Automatically link existing client profile if found or create a new one
    client = await crud.client.get_client_by_email(email=user_data.email, tenant_id=tenant_id)
    if client:
        if client.user_id is None:
            await crud.client.update_client(client_id=client.id, client_update={"user_id": user.id}, tenant_id=tenant_id)
    else:
        # Create a new client profile for the user
        await crud.client.create_client(client_data={
            "name": user_data.name,
            "email": user_data.email,
            "phone": user_data.phone,
            "user_id": user.id,
            "status": True
        }, tenant_id=tenant_id)

    return user


@router.get("/my-qr-token")
@limiter.limit("30 per minute")
async def get_my_qr_token(request: Request, current_user = Depends(get_current_user)):
    client = await crud.client.get_client_by_user_id(user_id=current_user.id)
    if not client:
        raise HTTPException(status_code=404, detail="No se encontró perfil de cliente asociado a tu cuenta")
    token = generate_qr_token(client.id)
    return {"token": token, "expires_in": 30}


@router.get("/my-pin")
@limiter.limit("30 per minute")
async def get_my_pin(request: Request, current_user = Depends(get_current_user)):
    client = await crud.client.get_client_by_user_id(user_id=current_user.id)
    if not client:
        raise HTTPException(status_code=404, detail="No se encontró perfil de cliente asociado a tu cuenta")
    pin = generate_pin(client.id)
    return {"pin": pin, "expires_in": 60}


@router.websocket("/ws/checkin/{user_id}")
async def ws_checkin(websocket: WebSocket, user_id: int):
    logger.info(f"[WS] Client connected for user_id={user_id}")
    await websocket.accept()
    try:
        async for event in subscribe_checkin(user_id):
            logger.info(f"[WS] Sending to user_id={user_id}: {event}")
            await websocket.send_json(event)
            break
    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected for user_id={user_id}")
    except Exception as e:
        logger.error(f"[WS] Error for user_id={user_id}: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
