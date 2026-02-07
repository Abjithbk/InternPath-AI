from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional, Dict

class SignupSchema(BaseModel):
    first_name: str
    second_name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthSchema(BaseModel):
    token: str

class InternshipOut(BaseModel):
    title: str
    company: str
    link: str
    source: str
    location: str
    duration: str
    stipend: str
    skills: str
    apply_by: date

    class Config:
        from_attributes = True

class UserProfileCreate(BaseModel):
    year : Optional[int] = None
    semester: Optional[int] = None
    college: Optional[str] = None
    course:Optional[str] = None
    cgpa: float | None = None
    skills: Optional[List[str]] = []
    projects:Optional[List[Dict]] = []

class UserProfileUpdate(BaseModel):
    year: Optional[int] = None
    semester: Optional[int] = None
    college: Optional[str] = None
    course: Optional[str] = None
    cgpa: float | None = None
    skills: Optional[List[str]] = None
    projects: Optional[List[Dict]] = None


class UserProfileOut(BaseModel):
    id: int
    user_id: int

    year: Optional[int]
    semester: Optional[int]
    college: Optional[str]
    course: Optional[str]
    cgpa:float
    skills: List[str]
    projects: List[Dict]

    class Config:
        from_attributes = True
