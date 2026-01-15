# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .database import Base

# ... (Keep your User class here) ...

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    link = Column(String, unique=True, nullable=False) # Prevents duplicates
    source = Column(String, default="Scraper")
    created_at = Column(DateTime(timezone=True), server_default=func.now())