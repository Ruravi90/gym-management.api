from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, WebSocket, WebSocketDisconnect, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
import logging
from app import crud, schemas
from app.utils.auth import (
    authenticate_user, create_access_token, create_refresh_token,
    verify_refresh_token, get_current_user,
    set_auth_cookies, clear_auth_cookies, REFRESH_TOKEN_COOKIE,
)
from app.config import settings
from app.middleware.security import limiter, auth_limits
from app.services.qr_service import generate_qr_token
from app.services.pin_service import generate_pin
from app.services.checkin_notifier import subscribe_checkin, notify_checkin
from app.models.user import User

logger = logging.getLogger(__name__)


router = APIRouter()

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

    user = await crud.user.create_user(user_data=user_dict)

    # Automatically link existing client profile if found or create a new one
    client = await crud.client.get_client_by_email(email=user_data.email)
    if client:
        if client.user_id is None:
            await crud.client.update_client(client_id=client.id, client_update={"user_id": user.id})
    else:
        # Create a new client profile for the user
        await crud.client.create_client(client_data={
            "name": user_data.name,
            "email": user_data.email,
            "phone": user_data.phone,
            "user_id": user.id,
            "status": True
        })

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
