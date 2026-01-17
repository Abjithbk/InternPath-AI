from sqlalchemy.orm import Session
from datetime import date
from . import models, scraper

# --- CONFIGURATION ---
TARGET_PER_SITE = 20  # Keeps 60 jobs total (20 Internshala + 20 Unstop + 20 Prosple)

# --- 1. CLEANUP EXPIRED JOBS ---
def delete_expired_jobs(db: Session):
    today = date.today()
    deleted = db.query(models.Internship).filter(
        models.Internship.apply_by != None,
        models.Internship.apply_by < today
    ).delete()
    db.commit()
    print(f"🧹 [Manager] Deleted {deleted} expired internships.")

# --- 2. CHECK & REFILL INVENTORY ---
async def maintain_pool(db: Session, keyword: str):
    print(f"🛡️ [Manager] Running inventory check for: '{keyword}'...")
    
    # A. Delete Expired First
    delete_expired_jobs(db)

    sources = ["Internshala", "Unstop", "Prosple"]
    report = {}

    for source in sources:
        # B. Count Current Inventory
        current_count = db.query(models.Internship).filter(
            models.Internship.source == source,
            models.Internship.keyword == keyword
        ).count()

        # C. Calculate Deficit
        needed = TARGET_PER_SITE - current_count

        if needed > 0:
            print(f"   ⚠️ [{source}] Low Inventory: Have {current_count}, Need {needed}. Refilling...")
            
            # D. Call Scraper with EXACT Limit
            if source == "Internshala":
                added = await scraper.scrape_internshala(keyword, db, limit=needed)
            elif source == "Unstop":
                added = await scraper.scrape_unstop(keyword, db, limit=needed)
            elif source == "Prosple":
                added = await scraper.scrape_prosple(keyword, db, limit=needed)
            
            report[source] = f"Added {added} new jobs"
        else:
            print(f"   ✅ [{source}] Inventory Full ({current_count}/{TARGET_PER_SITE}).")
            report[source] = "Full"

    return {"status": "Maintenance Complete", "report": report}