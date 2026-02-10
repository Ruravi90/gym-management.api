from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
from app import crud, schemas
from app.utils.auth import authenticate_user, create_access_token
from app.config import settings
from app.middleware.security import limiter, auth_limits


router = APIRouter()

@router.post("/login", response_model=schemas.Token)
@limiter.limit(auth_limits)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible login, get an access token for future requests.
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

    # Calculate expiration time
    expires_at = datetime.now(timezone.utc) + access_token_expires

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }

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
    return user