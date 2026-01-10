from pydantic import BaseModel, EmailStr

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
