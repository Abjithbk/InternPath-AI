from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from sqlalchemy import text, or_


from database import models, database
from dependencies import get_current_user
from services.request_cache import request_cache

router = APIRouter(prefix="/jobs", tags=["Internships"])


@lru_cache(maxsize=5000)
def _parse_skill_text(skill_text: str) -> frozenset[str]:
    if not skill_text:
        return frozenset()
    return frozenset(
        part.strip().lower()
        for part in skill_text.split(",")
        if part and part.strip()
    )


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---RUN ONCE IF DB IS BROKEN ---
@router.get("/fix-db")
def fix_database():
    try:
        with database.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS internships CASCADE"))
            conn.commit()

        models.Base.metadata.create_all(bind=database.engine)
        request_cache.delete_prefix("jobs:")
        return {"status": "success", "message": "Database rebuilt!"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# To get the internship details from database
@router.get("/")
async def get_internship_details(db: Session = Depends(get_db)):
    try:
        cache_key = "jobs:list"
        cached = request_cache.get(cache_key)
        if cached is not None:
            return cached

        internships = db.query(models.Internship).order_by(models.Internship.id.desc()).all()
        response = {"data": internships}
        request_cache.set(cache_key, response, ttl_seconds=120)
        return response
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Database error. Try again...")


# Filter endpoint

@router.get("/filter")
def filter_by_domain(domain: str,db:Session = Depends(get_db)):
    domain = domain.lower().strip()
    cache_key = f"jobs:filter:{domain}"
    cached = request_cache.get(cache_key)
    if cached is not None:
        return cached

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

    response = {
        "count":len(filtered),
        "data":filtered
    }
    request_cache.set(cache_key, response, ttl_seconds=120)
    return response

@router.get("/search")
def search_internship(q : str = Query(None,description="Search keyword"),db:Session = Depends(get_db)):
    normalized_q = (q or "").strip().lower()
    cache_key = f"jobs:search:{normalized_q or '__all__'}"
    cached = request_cache.get(cache_key)
    if cached is not None:
        return cached

    if q:
        results = (db.query(models.Internship).filter(models.Internship.title.ilike(f"%{q}%")).all())
    else:
        results = db.query(models.Internship).all()
    response = {
        "data":results
    }
    request_cache.set(cache_key, response, ttl_seconds=90)
    return response

@router.get("/recommendation")
def recommend_internship(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cache_key = f"jobs:recommend:{current_user.id}"
    cached = request_cache.get(cache_key)
    if cached is not None:
        return cached

    profile = db.query(models.UserProfile)\
        .filter(models.UserProfile.user_id == current_user.id)\
        .first()

    if not profile:
        return {"error": "Profile not found"}

    user_skills = {
        skill.strip().lower()
        for skill in (profile.skills or [])
        if skill and skill.strip()
    }

    if not user_skills:
        request_cache.set(cache_key, [], ttl_seconds=120)
        return []

    # Fetch only required columns (FASTER)
    conditions = [models.Internship.skills.ilike(f"%{skill}%") for skill in user_skills if len(skill) >= 2]

    internship_query = db.query(
        models.Internship.id,
        models.Internship.title,
        models.Internship.company,
        models.Internship.duration,
        models.Internship.location,
        models.Internship.link,
        models.Internship.skills,
        models.Internship.stipend
    )

    if conditions:
        internship_query = internship_query.filter(or_(*conditions))

    internships = internship_query.limit(1200).all()

    recommendations = []

    for internship in internships:
        required_skills = set(_parse_skill_text(internship.skills or ""))

        if not required_skills:
            continue

        match_count = len(user_skills & required_skills)
        match_percentage = int((match_count / len(required_skills)) * 100)

        # 🔥 Only push if some match exists (major performance improvement)
        if match_percentage > 0:
            recommendations.append({
                "id": internship.id,
                "title": internship.title,
                "company": internship.company,
                "duration": internship.duration,
                "location": internship.location,
                "link": internship.link,
                "skills": internship.skills,
                "stipend": internship.stipend,
                "match_percentage": match_percentage,
                "skill_gap": list(required_skills - user_skills)
            })

    # 🔥 Sort only matched ones
    recommendations = sorted(
        recommendations,
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    # 🔥 Limit results (VERY IMPORTANT)
    top_recommendations = recommendations[:20]
    request_cache.set(cache_key, top_recommendations, ttl_seconds=180)
    return top_recommendations