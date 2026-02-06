from sqlalchemy import Column, Integer, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class FacialEncoding(Base):
    __tablename__ = "facial_encodings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), unique=True)
    encoding_data = Column(LargeBinary) # Storing numpy array as bytes
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="facial_encoding")
