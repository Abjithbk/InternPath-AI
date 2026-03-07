import re

from pydantic import BaseModel, EmailStr, field_validator
from datetime import date,datetime
from typing import List, Optional, Dict
from typing import Dict

class SignupSchema(BaseModel):
    first_name: str
    second_name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must contain at least one special character")
        return password

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
    scraped_date: date

    class Config:
        from_attributes = True

class UserProfileCreate(BaseModel):
    year : Optional[int] = None
    semester: Optional[int] = None
    cgpa: float | None = None
    skills: Optional[List[str]] = []
    projects:Optional[List[Dict]] = []

class UserProfileUpdate(BaseModel):
    year: Optional[int] = None
    semester: Optional[int] = None
    cgpa: float | None = None
    skills: Optional[List[str]] = None
    projects: Optional[List[Dict]] = None


class UserProfileOut(BaseModel):
    id: int
    user_id: int

    year: Optional[int]
    semester: Optional[int]
    college: Optional[str]
    department: Optional[str]
    cgpa:float
    skills: List[str]
    projects: List[Dict]

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message : str
    session_id : Optional[int] = None

class ChatResponse(BaseModel):
    session_id:int
    response:str
    timestamp:datetime

    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class URLRequest(BaseModel):
    url: str



class ResumeAnalysisResponse(BaseModel):
    overall_score: int
    grade: str
    section_scores: Dict[str, float]
    linguistic_features: Dict[str, float]