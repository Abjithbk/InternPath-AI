# backend/scraper.py
import asyncio
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

async def scrape_internships(db: Session, keyword: str):
    print(f"🚀 [Scraper] Starting job search for: {keyword}")
    
    async with async_playwright() as p:
        # headless=True is CRITICAL for Render servers
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # We use 'We Work Remotely' as a reliable test target
        url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
        
        try:
            await page.goto(url)
            # Wait for the job list to appear
            await page.wait_for_selector("section.jobs", timeout=15000)
        except Exception as e:
            print(f"❌ [Scraper] Failed to load page: {e}")
            await browser.close()
            return {"status": "failed", "error": str(e)}

        # Scrape the items
        job_items = await page.query_selector_all("section.jobs li")
        jobs_added = 0

        for item in job_items:
            try:
                # Selectors for WeWorkRemotely
                title_el = await item.query_selector("span.title")
                company_el = await item.query_selector("span.company")
                link_el = await item.query_selector("a") # Link is usually on the parent or first anchor

                if title_el and company_el:
                    title = await title_el.inner_text()
                    company = await company_el.inner_text()
                    
                    # Extract Link
                    relative_link = await link_el.get_attribute("href") if link_el else ""
                    if relative_link.startswith("/"):
                        full_link = f"https://weworkremotely.com{relative_link}"
                    else:
                        full_link = relative_link

                    # --- DATABASE DEDUPLICATION ---
                    # Check if we already have this specific link
                    existing_job = db.query(models.Internship).filter(models.Internship.link == full_link).first()
                    
                    if not existing_job:
                        new_internship = models.Internship(
                            title=title,
                            company=company,
                            link=full_link,
                            source="We Work Remotely"
                        )
                        db.add(new_internship)
                        jobs_added += 1
            except Exception as e:
                # Ignore empty rows (headers/ads)
                continue

        # Save all new jobs
        db.commit()
        await browser.close()
        
        print(f"✅ [Scraper] Finished. Added {jobs_added} new jobs.")
        return {"status": "success", "new_jobs_count": jobs_added}