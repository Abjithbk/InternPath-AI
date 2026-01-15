# Add this to your imports at the top
from .scraper import scrape_internships

# Add this endpoint (e.g., after your /login route)
@app.post("/scrape-jobs")
async def trigger_scraper(keyword: str = "software intern", db: Session = Depends(get_db)):
    """
    Triggers the background scraper to find jobs and save them to the DB.
    """
    result = await scrape_internships(db, keyword)
    return result