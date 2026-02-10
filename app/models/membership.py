from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class MembershipType(Base):
    __tablename__ = "membership_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # "Day Pass", "Weekly", "Monthly", "Annual"
    duration_days = Column(Integer)  # 1 for day pass, 7 for weekly, 30 for monthly, 365 for annual
    accesses_allowed = Column(Integer, nullable=True)  # NULL means unlimited, specific number for punch passes
    price = Column(Float, nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = relationship("Membership", back_populates="membership_type")


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    membership_type_id = Column(Integer, ForeignKey("membership_types.id"))  # Reference to type
    type = Column(String(50))  # Kept for backward compatibility during migration
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    price = Column(Float)  # Original price
    price_paid = Column(Float)  # Actual price paid (may differ due to discounts)
    status = Column(String(20), default="active")  # active, expired, suspended, cancelled
    payment_status = Column(String(20), default="pending")  # pending, paid, overdue
    payment_method = Column(String(50))  # cash, card, bank_transfer, online
    accesses_used = Column(Integer, default=0)  # For punch-based memberships
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="memberships")
    membership_type = relationship("MembershipType", back_populates="memberships")
