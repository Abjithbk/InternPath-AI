from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, database, manager

# Initialize DB Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "InternPath Manager Active 🚀"}

@app.post("/refresh-pool")
async def refresh_internship_pool(keyword: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    AUTO-MAINTENANCE TRIGGER:
    1. Deletes expired jobs.
    2. Counts current jobs.
    3. Scrapes only what is needed to reach 20 per site.
    """
    background_tasks.add_task(manager.maintain_pool, db, keyword)
    return {"status": "Maintenance Started", "message": f"Manager is optimizing pool for '{keyword}'"}

@app.get("/jobs")
def get_jobs(keyword: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Internship)
    if keyword:
        query = query.filter(models.Internship.keyword == keyword)
    return query.order_by(models.Internship.id.desc()).all()