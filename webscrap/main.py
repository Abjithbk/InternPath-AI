from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from .scraper import scrape_internships

# 1. Create the database tables automatically
models.Base.metadata.create_all(bind=engine)

# 2. Initialize the FastAPI app (This was missing!)
app = FastAPI()

# 3. Define the Scraper Endpoint
@app.post("/scrape-jobs")
async def trigger_scraper(keyword: str = "software intern", db: Session = Depends(get_db)):
    """
    Triggers the background scraper to find jobs and save them to the DB.
    """
    try:
        result = await scrape_internships(db, keyword)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Root endpoint (Optional, for health check)
@app.get("/")
def read_root():
    return {"status": "Internship Scraper is running"}