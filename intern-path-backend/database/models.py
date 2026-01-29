from sqlalchemy import Column, Integer, String, Boolean,Date
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=True)
    is_google_user = Column(Boolean, default=False)

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String(200))
    company = Column(String(200))
    link = Column(String,unique=True,index=True)
    source = Column(String(50))
    keyword = Column(String(50), index=True)

    location = Column(String(100))
    duration = Column(String(50))
    stipend = Column(String(100))
    skills = Column(String(200))
    apply_by = Column(Date)
