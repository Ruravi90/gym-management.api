from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    type = Column(String(50))
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    price = Column(Float)
    status = Column(String(20), default="active")  # active, expired, suspended, cancelled
    payment_status = Column(String(20), default="pending")  # pending, paid, overdue
    payment_method = Column(String(50))  # cash, card, bank_transfer, online
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="memberships")
