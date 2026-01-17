from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, database, manager, scraper

# Initialize DB
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
    return {"status": "InternPath AI is Active 🧠"}

# --- 1. SMART SEARCH ENDPOINT (The Core Feature) ---
@app.get("/jobs")
async def get_jobs(keyword: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    1. Checks if we already have jobs for this keyword.
    2. If YES: Returns them instantly.
    3. If NO: Scrapes Internshala LIVE (wait 5s), returns data, 
       and triggers Unstop/Prosple in the background.
    """
    clean_keyword = keyword.lower().strip()
    
    # A. Check Database (Cache)
    existing_jobs = db.query(models.Internship).filter(
        models.Internship.keyword == clean_keyword
    ).order_by(models.Internship.id.desc()).all()
    
    # B. If we have enough data (Cache Hit) -> Return it
    if len(existing_jobs) >= 5:
        return existing_jobs

    # C. If Database is Empty (Cold Start) -> Scrape NOW
    print(f"❄️ [Cold Start] New topic '{clean_keyword}' detected. Scraping live...")
    
    # Run Internshala immediately (await) so user gets results NOW
    # Limit to 10 to keep it fast (3-5 seconds)
    await scraper.scrape_internshala(clean_keyword, db, limit=10)
    
    # D. Trigger other sites in background (Don't make user wait)
    # They will populate the DB over the next minute
    background_tasks.add_task(scraper.scrape_unstop, clean_keyword, db, limit=10)
    background_tasks.add_task(scraper.scrape_prosple, clean_keyword, db, limit=10)

    # E. Return the fresh data we just scraped
    new_jobs = db.query(models.Internship).filter(
        models.Internship.keyword == clean_keyword
    ).order_by(models.Internship.id.desc()).all()
    
    return new_jobs

# --- 2. DAILY MAINTENANCE TRIGGER ---
@app.post("/refresh-pool")
async def refresh_all_pools(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger this via Cron-Job.org every night.
    It automatically finds ALL keywords users have searched for
    and refreshes them.
    """
    background_tasks.add_task(manager.maintain_all_pools, db)
    return {"status": "Maintenance Started", "message": "Updating ALL user profiles in background."}

# --- 3. UTILS ---
@app.get("/force-reset-db")
def force_reset_db():
    try:
        models.Base.metadata.drop_all(bind=database.engine)
        models.Base.metadata.create_all(bind=database.engine)
        return {"status": "SUCCESS", "message": "DB Wiped & Recreated."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}