from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ..database import Base
# from sqlalchemy.orm import relationship

class GymClass(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    instructor = Column(String(100))
    schedule = Column(DateTime) # Simple datetime for now, could be cron string or complex schedule
    capacity = Column(Integer)
