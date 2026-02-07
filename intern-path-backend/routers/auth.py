from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import User
from database.schemas import SignupSchema,LoginSchema,GoogleAuthSchema
from security import hash_password,verify_password,create_access_token
from routers.google_auth import handle_google_signup_or_login

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def manual_signup(data: SignupSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)

    user = User(
        first_name=data.first_name,
        second_name=data.second_name,
        email=data.email,
        password=hashed,
        is_google_user=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    full_name = f"{user.first_name} {user.second_name}".strip()
    token = create_access_token(
        data={
            "sub":str(user.id),
            "username":full_name,
            "email":user.email
        }
    )
    return {
        "access_token":token
    }

@router.post("/login")
def manual_login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_google_user:
        raise HTTPException(status_code=400, detail="Use Google Sign-In for this account")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id),"username":f"{user.first_name} {user.second_name}","email":user.email})
    return {"access_token": token}

@router.post("/google-auth")
def google_signup_or_login(data: GoogleAuthSchema, db: Session = Depends(get_db)):
    return handle_google_signup_or_login(data.token, db)