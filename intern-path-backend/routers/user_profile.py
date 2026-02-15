from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from database import database
from database.models import UserProfile
from database.schemas import (
    UserProfileCreate,
    UserProfileOut,
    UserProfileUpdate
)
from dependencies import get_current_user

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
router = APIRouter(prefix="/profile",tags=["User Profile"])

@router.post("/",response_model=UserProfileOut,status_code=status.HTTP_201_CREATED)

def create_user_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    existing = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User Profile already exits"
        )
    new_profile = UserProfile (
        user_id = current_user.id,
        year=profile.year,
        semester=profile.semester,
        college=profile.college,
        department=profile.department,
        cgpa=profile.cgpa,
        skills=profile.skills or [],
        projects=profile.projects or []
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@router.get("/",response_model=UserProfileOut)

def get_user_profile(
    db:Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )
    return profile

@router.put("/",response_model=UserProfileUpdate)

def update_user_profile(
    profile:UserProfileUpdate,
    db:Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_profile  = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not db_profile:
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )
    
    updated_data = profile.model_dump(exclude_unset=True)

    if "skills" in updated_data:
        db_profile.skills = list(set(db_profile.skills+updated_data["skills"]))
    if "projects" in updated_data:
        db_profile.projects.extend(updated_data["projects"])

    for field,value in updated_data.items():
        if field not in ["skills","projects"]:
            setattr(db_profile,field,value)

    db.commit()
    db.refresh(db_profile)
    return db_profile