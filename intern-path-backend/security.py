import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt, JWTError,ExpiredSignatureError
from dotenv import load_dotenv
from fastapi import Header,HTTPException,status

load_dotenv()

# Configuration from Environment Variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this")
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 24 hours

# --- Password Hashing (Using bcrypt directly) ---

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT Token Handling ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a signed JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """
    Decodes and validates a JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return "expired"
    except JWTError:
        return None
    
def verify_scraper_key(x_api_key:str = Header(...)):
    #its for protecting the automation endpoints

    if not SCRAPER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="SCRAPER_API_KEY not set in environment"
        )
    if x_api_key != SCRAPER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid automation key"
        )