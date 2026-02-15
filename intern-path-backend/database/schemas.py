from pydantic import BaseModel, EmailStr
from datetime import date,datetime
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
    department:Optional[str] = None
    cgpa: float | None = None
    skills: Optional[List[str]] = []
    projects:Optional[List[Dict]] = []

class UserProfileUpdate(BaseModel):
    year: Optional[int] = None
    semester: Optional[int] = None
    college: Optional[str] = None
    department: Optional[str] = None
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