from pydantic import BaseModel, EmailStr
from datetime import date

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