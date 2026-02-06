from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum

class MembershipType(str, enum.Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    VIP = "vip"
    STUDENT = "student"
    FAMILY = "family"

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    membership_type = Column(String(20), default=MembershipType.BASIC)
    profile_image = Column(String(255), nullable=True)  # Path to profile image for facial recognition
    status = Column(Boolean, default=True)  # Active/inactive client
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendance = relationship("Attendance", back_populates="client")
    memberships = relationship("Membership", back_populates="client")
    facial_encoding = relationship("FacialEncoding", back_populates="client", uselist=False)