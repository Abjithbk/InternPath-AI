import sys
import asyncio
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import models, database
from scraper import intershala as scraper
from dependencies import get_current_user
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


# To get the internship details from database
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
async def get_jobs(db: Session = Depends(get_db)):
    try:
        # No query needed — scraper will handle predefined keywords internally
        total_saved = await scraper.scrape_internshala(db, limit=10)
        return {"source": "live", "total_saved": total_saved}
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

@router.get("/recommendation")
def recommend_internship(
    db:Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()

    if not profile:
        return {
            "error":"Profile not found"
        }
    
    user_skills = set(skill.strip().lower() for skill in profile.skills)
    internships = db.query(models.Internship).all()

    recommendations = []

    for internship in internships:
        required_skills = set(skill.strip().lower() for skill in internship.skills.split(","))
        match_count = len(user_skills & required_skills)
        total_required = len(required_skills)
        match_percentage = int((match_count/total_required) * 100) if total_required > 0 else 0

        skill_gap = list(required_skills - user_skills)

        recommendations.append({
            "id":internship.id,
            "title":internship.title,
            "company":internship.company,
            "duration":internship.duration,
            "location":internship.location,
            "link":internship.link,
            "skills":internship.skills,
            "stipend":internship.stipend,
            "match_percentage":match_percentage,
            "skill_gap":skill_gap
        })

    recommendations.sort(key = lambda x:x["match_percentage"],reverse=True)
    return recommendations