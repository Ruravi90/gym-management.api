"""
BCrypt fix for handling passwords longer than 72 bytes.
This module provides a wrapper around bcrypt to handle long passwords.
"""
import bcrypt
from passlib.context import CryptContext

# Create a password context that handles long passwords
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__rounds=12,
)

def hash_password(password: str) -> str:
    """Hash a password, truncating if longer than 72 bytes to comply with bcrypt limits."""
    # Bcrypt has a 72-byte password limit, so truncate if necessary
    if len(password.encode('utf-8')) > 72:
        # Truncate to 72 bytes while preserving character boundaries
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash, handling long passwords."""
    # If the plain password is too long, truncate it for comparison
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


# Explicitly define what should be exported when this module is imported
__all__ = ['hash_password', 'verify_password']
