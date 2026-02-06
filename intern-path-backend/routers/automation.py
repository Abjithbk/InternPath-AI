from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import database,models
from scraper import intershala as scraper
from security import verify_scraper_key

router = APIRouter(prefix="/automation",tags=["Automation"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    except:
        db.close()

@router.post
async def scrape_weekly(
    db: Session = Depends(get_db),
    _: None = Depends(verify_scraper_key)
):
    keywords = [
        "python",
        "react",
        "backend",
        "frontend",
        "ai",
        "data science"
    ]

    total_scraped = 0

    for keyword in keywords:
        print(f"🚀 Scraping keyword: {keyword}")

        count = await scraper.scrape_internshala(
            keyword=keyword,
            db=db,
            limit=15
        )
        total_scraped += count

    return {
        "status": "success",
        "keywords": keywords,
        "total_scraped": total_scraped
    }


# ---------- DANGEROUS: DB RESET ----------
@router.post("/fix-db")
def fix_database(
    _: None = Depends(verify_scraper_key)  # 🔐 PROTECTED
):
    try:
        with database.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS internships CASCADE"))
            conn.commit()

        models.Base.metadata.create_all(bind=database.engine)

        return {
            "status": "success",
            "message": "Database rebuilt successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))