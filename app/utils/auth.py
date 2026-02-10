import bcrypt

def hash_password_bcrypt_fix(password: str) -> str:
    """Hash a password, preprocessing if longer than 72 bytes to comply with bcrypt limits."""
    # Bcrypt has a 72-byte password limit, so preprocess if necessary
    # Ensure we're working with bytes and truncate at 72 bytes max
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to exactly 72 bytes and decode back to string
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    # Use bcrypt directly to hash the password
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password_bcrypt_fix(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash, handling long passwords."""
    # Ensure we're working with bytes and truncate at 72 bytes max before passing to bcrypt
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to exactly 72 bytes and decode back to string
        password_bytes = password_bytes[:72]
        plain_password = password_bytes.decode('utf-8', errors='ignore')

    # Use bcrypt directly to verify the password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.models.user import User

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return verify_password_bcrypt_fix(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash a plain password using the bcrypt fix."""
    return hash_password_bcrypt_fix(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload if valid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user = await User.get_or_none(id=int(user_id))
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    try:
        user = await User.get_or_none(email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception:
        return None