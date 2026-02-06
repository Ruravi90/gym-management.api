from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from .user_role import UserRole
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    role = Column(String(20), default=UserRole.MEMBER)  # Role of the user in the system
    hashed_password = Column(String(100))
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    # Note: Users don't have direct relationships to attendance, memberships, or facial encodings
    # These belong to clients, not system users
