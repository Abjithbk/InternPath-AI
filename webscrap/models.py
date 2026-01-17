from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from .database import Base

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    link = Column(String, unique=True, index=True)
    source = Column(String, index=True)
    
    # --- PROFILING & FILTERING ---
    keyword = Column(String, index=True) # e.g. "software"
    
    # --- DETAILS ---
    location = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    stipend = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    
    # --- AUTO-DELETION ---
    apply_by = Column(Date, nullable=True) # Stores YYYY-MM-DD
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())