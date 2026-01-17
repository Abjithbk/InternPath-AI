from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, database, manager, scraper

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

# --- 1. SMART SEARCH (User Triggered) ---
@app.get("/jobs")
async def get_jobs(keyword: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    clean_keyword = keyword.lower().strip()
    
    # Check Cache
    existing = db.query(models.Internship).filter(models.Internship.keyword == clean_keyword).order_by(models.Internship.id.desc()).all()
    
    # Cache Hit (We have data)
    if len(existing) >= 5: return existing

    # Cold Start (Scrape NOW)
    print(f"❄️ [Cold Start] New topic '{clean_keyword}'. Scraping live...")
    await scraper.scrape_internshala(clean_keyword, db, limit=10) # Wait for this
    
    # Background fill for others
    background_tasks.add_task(scraper.scrape_unstop, clean_keyword, db, limit=10)
    background_tasks.add_task(scraper.scrape_prosple, clean_keyword, db, limit=10)

    # Return new data
    return db.query(models.Internship).filter(models.Internship.keyword == clean_keyword).all()

# --- 2. NIGHTLY TRIGGER (Cron Job) ---
@app.post("/refresh-pool")
async def refresh_all_pools(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(manager.maintain_all_pools, db)
    return {"status": "Maintenance Started"}

# --- 3. RESET BUTTON (Fixes DB Errors) ---
@app.get("/force-reset-db")
def force_reset_db():
    try:
        models.Base.metadata.drop_all(bind=database.engine)
        models.Base.metadata.create_all(bind=database.engine)
        return {"status": "SUCCESS", "message": "DB Wiped & Recreated."}
    except Exception as e: return {"status": "ERROR", "message": str(e)}