from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import SessionLocal
from services.profile_score import score_user_profile

router = APIRouter(prefix="/score", tags=["Scoring"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}")
def score_user(user_id: int, db: Session = Depends(get_db)):

    row = db.execute(
        text("""
            SELECT college, course, cgpa, skills, projects
            FROM userprofile
            WHERE id = :id
        """),
        {"id": user_id}
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return score_user_profile(dict(row._mapping))