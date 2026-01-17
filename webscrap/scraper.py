import asyncio
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

async def scrape_internships(db: Session, keyword: str):
    print(f"🚀 [Scraper] Starting job search for: {keyword}")
    
    async with async_playwright() as p:
        # --- 1. RENDER SERVER CONFIGURATION ---
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

        # --- 2. CONTEXT SETUP (Anti-Blocking) ---
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Target URL
        url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
        
        try:
            print(f"🌍 [Scraper] Navigating to: {url}")
            await page.goto(url, timeout=60000)
            
            # Print title for debugging
            page_title = await page.title()
            print(f"📄 [Scraper] Page Title is: '{page_title}'")

            # Check if we were blocked
            if "Just a moment" in page_title or "Cloudflare" in page_title:
                print("⚠️ [Scraper] BLOCKED by Cloudflare protection.")
                await browser.close()
                return {"status": "blocked", "error": "Cloudflare detected"}

            # --- 3. SMART WAIT LOGIC ---
            # Wait for the main container to ensure page loaded
            try:
                await page.wait_for_selector("div.content", timeout=30000)
            except:
                print("⚠️ [Scraper] Main content not found. Page might be blank.")

            # Check if jobs exist
            jobs_section = await page.query_selector("section.jobs")
            
            if not jobs_section:
                print("⚠️ [Scraper] No jobs found for this keyword. (0 results)")
                await browser.close()
                return {"status": "success", "new_jobs_count": 0, "message": "No jobs found"}

        except Exception as e:
            print(f"❌ [Scraper] Navigation failed: {e}")
            await browser.close()
            return {"status": "failed", "error": str(e)}

        # --- 4. PARSE JOBS ---
        job_items = await page.query_selector_all("section.jobs li")
        print(f"🔍 [Scraper] Found {len(job_items)} potential items. Parsing...")
        
        jobs_added = 0
        for item in job_items:
            try:
                # Selectors for WeWorkRemotely
                title_el = await item.query_selector("span.title")
                company_el = await item.query_selector("span.company")
                link_el = await item.query_selector("a")

                if title_el and company_el:
                    title = await title_el.inner_text()
                    company = await company_el.inner_text()
                    
                    # Extract Link
                    relative_link = await link_el.get_attribute("href") if link_el else ""
                    if relative_link.startswith("/"):
                        full_link = f"https://weworkremotely.com{relative_link}"
                    else:
                        full_link = relative_link

                    # --- 5. SAVE TO DB ---
                    # Check duplicate
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
                # Ignore empty rows or ads
                continue

        db.commit()
        await browser.close()
        
        print(f"✅ [Scraper] Finished. Added {jobs_added} new jobs.")
        return {"status": "success", "new_jobs_count": jobs_added}