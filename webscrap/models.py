# backend/models.py
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from .database import Base

class Internship(Base):
    __tablename__ = "internships"

<<<<<<< HEAD
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
=======
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(100), nullable=False, index=True)
    link = Column(String, unique=True, nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)
    keyword = Column(String(100), nullable=False, index=True)

    location = Column(String(100), nullable=True)
    duration = Column(String(50), nullable=True)
    stipend = Column(String(100), nullable=True)
    skills = Column(String(200), nullable=True)

    apply_by = Column(Date, nullable=True)
<<<<<<< HEAD
=======
>>>>>>> c4ba0b2 (Ameyaaa)
>>>>>>> 60cdc0098c26736ebccc4cbd23c4830ca28c61d1
    created_at = Column(DateTime(timezone=True), server_default=func.now())
