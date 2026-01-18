from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from .database import Base

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    company = Column(String(100), nullable=False)
    link = Column(String, unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    keyword = Column(String(100), nullable=False)
    location = Column(String(100))
    duration = Column(String(50))
    stipend = Column(String(100))
    skills = Column(String(200))
    apply_by = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
