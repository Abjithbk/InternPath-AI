import sys
import asyncio
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import models, database
from scraper import intershala as scraper

# Fix for Windows event loop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

router = APIRouter(prefix="/jobs", tags=["Internships"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 🛠️ RUN ONCE IF DB IS BROKEN ---
@router.get("/fix-db")
def fix_database():
    try:
        with database.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS internships CASCADE"))
            conn.commit()

        models.Base.metadata.create_all(bind=database.engine)
        return {"status": "success", "message": "Database rebuilt!"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/")
async def get_internship_details(db: Session = Depends(get_db)):
    try:
        # Fetch every internship in the database
        # order_by(models.Internship.id.desc()) ensures the newest data is at the top
        internships = db.query(models.Internship).order_by(models.Internship.id.desc()).all()
        
        return {"data": internships}
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Database error. Try again...")

# --- 🔍 MAIN SEARCH ENDPOINT ---
@router.get("/scrape")
async def get_jobs(query: str, db: Session = Depends(get_db)):
    clean_keyword = query.lower().strip()

    # 1️⃣ FETCH CACHE
    try:
        cached_jobs = (
            db.query(models.Internship)
            .filter(models.Internship.keyword == clean_keyword)
            .limit(20)
            .all()
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database broken. Visit /jobs/fix-db"
        )

    # 2️⃣ VALIDATE CACHE
    has_data = len(cached_jobs) >= 5
    has_real_skills = any(
        job.skills not in ["N/A", "Loading...", "View Details"]
        for job in cached_jobs
    )

    if has_data and has_real_skills:
        print(f"✅ Serving cached data for '{clean_keyword}'")
        return {"source": "cache", "data": cached_jobs}

    # 3️⃣ SCRAPE LIVE
    print(f"❄️ Cache invalid. Scraping for '{clean_keyword}'")

    try:
        count = await scraper.scrape_internshala(
            clean_keyword,
            db,
            limit=10
        )
        new_data = (
            db.query(models.Internship)
            .filter(models.Internship.keyword == clean_keyword)
            .all()
        )
        return {"source": "live", "count": count, "data": new_data}

    except Exception as e:
        print(f"🔥 Scraper error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Filter endpoint

@router.get("/filter")
def filter_by_domain(domain: str,db:Session = Depends(get_db)):
    domain = domain.lower().strip()

    domain_keywords = {
        "ai": ["ai", "artificial intelligence", "ml", "machine learning", "llm", "nlp"],
        "web": ["web", "frontend", "backend", "full stack", "react", "django", "html", "css", "javascript"],
        "data": ["data", "pandas", "numpy", "sql", "analytics"],
        "mobile": ["android", "ios", "flutter", "react native"]
    }

    if domain not in domain_keywords:
        raise HTTPException(status_code=400,detail="Invalid domain")
    keywords = domain_keywords[domain]
    internships = db.query(models.Internship).all()

    filtered = []

    for job in internships:
        text = f"{job.title} {job.skills}".lower()
        if any(k in text for k in keywords):
            filtered.append(job)

    return {
        "count":len(filtered),
        "data":filtered
    }

@router.get("/search")
def search_internship(q : str = Query(None,description="Search keyword"),db:Session = Depends(get_db)):
    if q:
        results = (db.query(models.Internship).filter(models.Internship.title.ilike(f"%{q}%")).all())
    else:
        results = db.query(models.Internship).all()
    return {
        "data":results
    }    