from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app import crud, schemas
from app.database import get_db
from app.utils.auth import authenticate_user, create_access_token
from app.config import settings
from app.middleware.security import limiter, auth_limits

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
@limiter.limit(auth_limits)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible login, get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
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
    from datetime import datetime
    expires_at = datetime.utcnow() + access_token_expires

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }

@router.post("/register", response_model=schemas.User)
@limiter.limit(auth_limits)
def register(request: Request, user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = crud.user.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with hashed password
    user_create = schemas.UserCreate(
        email=user_data.email,
        name=user_data.name,
        phone=user_data.phone,
        membership_type=user_data.membership_type,
        password=user_data.password
    )

    user = crud.user.create_user(db=db, user=user_create)
    return user