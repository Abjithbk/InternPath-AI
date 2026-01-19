from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Local imports (Works when Root Directory = backend)
from database import SessionLocal, engine
import models
from schemas import SignupSchema, LoginSchema, GoogleAuthSchema
from security import hash_password, verify_password, create_access_token
from google_auth import handle_google_signup_or_login

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS so Frontend can talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/signup")
def manual_signup(data: SignupSchema, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)

    user = models.User(
        first_name=data.first_name,
        second_name=data.second_name,
        email=data.email,
        password=hashed,
        is_google_user=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Signup successful"}

@app.post("/login")
def manual_login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_google_user:
        raise HTTPException(status_code=400, detail="Use Google Sign-In for this account")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token}

@app.post("/google-auth")
def google_signup_or_login(data: GoogleAuthSchema, db: Session = Depends(get_db)):
    return handle_google_signup_or_login(data.token, db)