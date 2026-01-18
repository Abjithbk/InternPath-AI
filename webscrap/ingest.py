from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from .database import SessionLocal
from .models import Internship
from .security import verify_ingest_key

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ingest", dependencies=[Depends(verify_ingest_key)])
def ingest(jobs: list[dict], db: Session = Depends(get_db)):
    saved = 0
    for job in jobs:
        if db.query(Internship).filter_by(link=job["link"]).first():
            continue

        job["apply_by"] = job.get("apply_by") or date.today() + timedelta(days=14)
        db.add(Internship(**job))
        db.commit()
        saved += 1

    return {"saved": saved}
