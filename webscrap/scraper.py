import asyncio
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

async def scrape_internships(db: Session, keyword: str):
    print(f"🚀 [Scraper] Starting job search for: {keyword}")
    
    async with async_playwright() as p:
        browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
        
        print("🚀 [Scraper] Launching browser...")
        try:
            browser = await p.chromium.launch(headless=True, args=browser_args)
            print("✅ [Scraper] Browser launched successfully!")
        except Exception as e:
            print(f"❌ [Scraper] CRITICAL ERROR: Could not launch browser. Details: {e}")
            raise e

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Target URL
        url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
        
        try:
            print(f"🌍 [Scraper] Navigating to: {url}")
            await page.goto(url, timeout=60000) # Increased timeout to 60s
            
            # --- DEBUGGING: Print the Page Title ---
            page_title = await page.title()
            print(f"📄 [Scraper] Page Title is: '{page_title}'")
            
            if "Just a moment" in page_title or "Cloudflare" in page_title:
                print("⚠️ [Scraper] BLOCKED by Cloudflare protection.")
                await browser.close()
                return {"status": "blocked", "error": "Cloudflare detected"}

            # Wait for the job list (Increased to 30s)
            await page.wait_for_selector("section.jobs", timeout=30000)
            
        except Exception as e:
            print(f"❌ [Scraper] Failed to load page: {e}")
            # Optional: Print page source snippet to debug
            content = await page.content()
            print(f"📄 [Scraper] Page content snippet: {content[:500]}")
            await browser.close()
            return {"status": "failed", "error": str(e)}

        # Scrape the items
        job_items = await page.query_selector_all("section.jobs li")
        print(f"🔍 [Scraper] Found {len(job_items)} potential jobs. Parsing...")
        
        jobs_added = 0
        for item in job_items:
            try:
                title_el = await item.query_selector("span.title")
                company_el = await item.query_selector("span.company")
                link_el = await item.query_selector("a")

                if title_el and company_el:
                    title = await title_el.inner_text()
                    company = await company_el.inner_text()
                    relative_link = await link_el.get_attribute("href") if link_el else ""
                    full_link = f"https://weworkremotely.com{relative_link}" if relative_link.startswith("/") else relative_link

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
            except Exception:
                continue

        db.commit()
        await browser.close()
        
        print(f"✅ [Scraper] Finished. Added {jobs_added} new jobs.")
        return {"status": "success", "new_jobs_count": jobs_added}