from sqlalchemy.orm import Session
from datetime import date
from . import models, scraper

TARGET_PER_SITE = 20 

def delete_expired_jobs(db: Session):
    """Deletes jobs where Deadline < Today"""
    today = date.today()
    deleted = db.query(models.Internship).filter(
        models.Internship.apply_by != None,
        models.Internship.apply_by < today
    ).delete()
    db.commit()
    print(f"🧹 [Manager] Deleted {deleted} expired internships.")

async def maintain_pool(db: Session, keyword: str):
    """Ensures we have 20 jobs per site for this keyword"""
    sources = ["Internshala", "Unstop", "Prosple"]
    for source in sources:
        current = db.query(models.Internship).filter(
            models.Internship.source == source,
            models.Internship.keyword == keyword
        ).count()

        needed = TARGET_PER_SITE - current

        if needed > 0:
            print(f"   ⚠️ [{keyword}] {source}: Need {needed}. Refilling...")
            if source == "Internshala": await scraper.scrape_internshala(keyword, db, limit=needed)
            elif source == "Unstop": await scraper.scrape_unstop(keyword, db, limit=needed)
            elif source == "Prosple": await scraper.scrape_prosple(keyword, db, limit=needed)

async def maintain_all_pools(db: Session):
    """Auto-Discovers all user keywords and refreshes them"""
    active_keywords = [r[0] for r in db.query(models.Internship.keyword).distinct() if r[0]]
    print(f"🚀 [Auto-Pilot] Maintaining {len(active_keywords)} profiles: {active_keywords}")
    
    delete_expired_jobs(db)
    
    for kw in active_keywords:
        await maintain_pool(db, kw)