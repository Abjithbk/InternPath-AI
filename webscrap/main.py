from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles 
from sqlalchemy.orm import Session
from . import models, database, manager, scraper

# Ensure DB tables exist
models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- HELPER: BACKGROUND SEQUENCE (RAM SAFE) ---
async def background_fill_sequence(keyword: str):
    """
    Runs scrapers one-by-one with a FRESH session.
    ORDER: Prosple (2nd) -> Unstop (3rd)
    """
    print(f"🕵️ [Background] Starting Sequence for '{keyword}'...")
    db = database.SessionLocal()
    try:
        # Priority 2: Run Prosple
        # We run this first in background because it's usually faster than Unstop
        await scraper.scrape_prosple(keyword, db, limit=10)
        
        # Priority 3: Run Unstop
        # Runs last because it's the heaviest SPA
        await scraper.scrape_unstop(keyword, db, limit=10)
        
    except Exception as e:
        print(f"❌ Bg Error: {e}")
    finally:
        db.close()

# --- HELPER: MAINTENANCE SEQUENCE (RAM SAFE) ---
async def run_maintenance_safe():
    db = database.SessionLocal()
    try:
        await manager.maintain_all_pools(db)
    finally:
        db.close()

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/jobs")
async def get_jobs(keyword: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    clean_keyword = keyword.lower().strip()
    
    # 1. Check Cache (Instant)
    existing = db.query(models.Internship).filter(models.Internship.keyword == clean_keyword).order_by(models.Internship.id.desc()).all()
    
    if len(existing) >= 5:
        return existing

    # 2. Cold Start (If cache empty)
    print(f"❄️ [Cold Start] New topic '{clean_keyword}'. Scraping live...")
    
    # Priority 1: Internshala (Foreground)
    # The user waits ~4-5 seconds for this, so they get data immediately.
    await scraper.scrape_internshala(clean_keyword, db, limit=10)
    
    # Trigger Background Sequence (Prosple -> Unstop)
    background_tasks.add_task(background_fill_sequence, clean_keyword)

    # Return whatever we found from Internshala immediately
    return db.query(models.Internship).filter(models.Internship.keyword == clean_keyword).all()

@app.post("/refresh-pool")
async def refresh_all_pools(background_tasks: BackgroundTasks):
    """Trigger this via Cron Job every night"""
    background_tasks.add_task(run_maintenance_safe)
    return {"status": "Maintenance Started"}

@app.get("/force-reset-db")
def force_reset_db():
    try:
        models.Base.metadata.drop_all(bind=database.engine)
        models.Base.metadata.create_all(bind=database.engine)
        return {"status": "SUCCESS", "message": "DB Wiped & Recreated."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}