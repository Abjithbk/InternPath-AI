from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, database, manager, scraper

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

# --- HELPER: BACKGROUND SEQUENCE (RAM SAFE) ---
async def background_fill_sequence(keyword: str):
    """Runs scrapers one-by-one with a FRESH session"""
    print(f"🕵️ [Background] Filling '{keyword}'...")
    db = database.SessionLocal()
    try:
        await scraper.scrape_unstop(keyword, db, limit=10)
        await scraper.scrape_prosple(keyword, db, limit=10)
    except Exception as e: print(f"❌ Bg Error: {e}")
    finally: db.close()

# --- HELPER: MAINTENANCE SEQUENCE (RAM SAFE) ---
async def run_maintenance_safe():
    db = database.SessionLocal()
    try: await manager.maintain_all_pools(db)
    finally: db.close()

# --- ENDPOINTS ---
@app.get("/")
def read_root(): return {"status": "InternPath AI Active 🧠"}

@app.get("/jobs")
async def get_jobs(keyword: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    clean_keyword = keyword.lower().strip()
    
    # Check Cache
    existing = db.query(models.Internship).filter(models.Internship.keyword == clean_keyword).order_by(models.Internship.id.desc()).all()
    if len(existing) >= 5: return existing

    # Cold Start
    print(f"❄️ [Cold Start] New topic '{clean_keyword}'...")
    await scraper.scrape_internshala(clean_keyword, db, limit=10)
    
    # Trigger Safe Background Sequence
    background_tasks.add_task(background_fill_sequence, clean_keyword)

    return db.query(models.Internship).filter(models.Internship.keyword == clean_keyword).all()

@app.post("/refresh-pool")
async def refresh_all_pools(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_maintenance_safe)
    return {"status": "Maintenance Started"}

@app.get("/force-reset-db")
def force_reset_db():
    try:
        models.Base.metadata.drop_all(bind=database.engine)
        models.Base.metadata.create_all(bind=database.engine)
        return {"status": "SUCCESS"}
    except Exception as e: return {"status": "ERROR", "message": str(e)}