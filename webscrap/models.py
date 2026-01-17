from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    link = Column(String, unique=True, index=True) # Unique link prevents duplicates
    source = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())