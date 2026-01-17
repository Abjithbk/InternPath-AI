from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database, scraper
import random

# Initialize DB
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "InternPath AI Scraper is Live 🚀"}

@app.post("/scrape-jobs")
async def trigger_scrape(keyword: str, db: Session = Depends(get_db)):
    return await scraper.scrape_internships(db, keyword)

@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(models.Internship).order_by(models.Internship.id.desc()).limit(100).all()

# --- DB CONNECTION TEST TOOL ---
@app.get("/test-db-connection")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Create a Fake Job to test writing
        test_job = models.Internship(
            title="TEST CONNECTION JOB",
            company="Supabase Check",
            link=f"https://test.com/{random.randint(1000,9999)}",
            source="System Test"
        )
        db.add(test_job)
        db.commit()
        db.refresh(test_job)
        
        return {"status": "SUCCESS", "message": "Successfully wrote to Supabase!", "job_id": test_job.id}
    except Exception as e:
        return {"status": "FAILURE", "error": str(e), "hint": "Check DATABASE_URL in Render."}