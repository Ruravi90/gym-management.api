"""
Centralized bcrypt compatibility patches.

This module must be imported BEFORE any passlib or bcrypt usage.
It fixes two known issues:
1. passlib compatibility with bcrypt 4.0+ (missing __about__)
2. bcrypt ValueError when password exceeds 72 bytes
"""
import bcrypt

# Fix for passlib compatibility with bcrypt 4.0+
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (object,), {"__version__": bcrypt.__version__})

# Fix for ValueError: password cannot be longer than 72 bytes
_original_hashpw = bcrypt.hashpw

def _patched_hashpw(password, salt):
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return _original_hashpw(password_bytes, salt)

bcrypt.hashpw = _patched_hashpw
