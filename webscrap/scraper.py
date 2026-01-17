import asyncio
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

# --- CONFIGURATION ---
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu"
]

# Use a real user agent to look like a human on Internshala
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ==========================================
# SITE 1: INTERNSHALA (The #1 Indian Source)
# ==========================================
async def scrape_internshala(page, keyword, db):
    print(f"   👉 [Internshala] Navigating to search...")
    # Internshala URL pattern: internshala.com/internships/keywords-<term>
    formatted_keyword = keyword.replace(" ", "-")
    url = f"https://internshala.com/internships/keywords-{formatted_keyword}"
    
    try:
        await page.goto(url, timeout=60000)
        # Wait for the specific container Internshala uses
        await page.wait_for_selector("div.individual_internship", timeout=15000)
    except:
        print("   ⚠️ [Internshala] No internships found or blocked.")
        return 0

    job_cards = await page.query_selector_all("div.individual_internship")
    count = 0
    
    for card in job_cards:
        try:
            # Internshala ID helps us avoid ads
            internship_id = await card.get_attribute("internshipid")
            if not internship_id: continue

            # Selectors
            title_el = await card.query_selector("h3.job-title") or await card.query_selector(".profile")
            company_el = await card.query_selector("div.company_name") or await card.query_selector(".link_display_like_text")
            link_el = await card.query_selector("a.view_detail_button") # The explicit button

            if not link_el: 
                # Fallback: sometimes the whole card is a link, or title is a link
                link_el = await card.query_selector("a")

            title = await title_el.inner_text()
            company = await company_el.inner_text()
            relative_link = await link_el.get_attribute("href")
            full_link = f"https://internshala.com{relative_link}"
            
            # Clean up company name (Internshala often adds whitespace)
            company = company.strip()

            if save_job(db, title, company, full_link, "Internshala"):
                count += 1
        except Exception as e:
            continue

    print(f"   ✅ [Internshala] Found {count} new internships.")
    return count

# ==========================================
# SITE 2: UNSTOP (Formerly Dare2Compete)
# ==========================================
async def scrape_unstop(page, keyword, db):
    print(f"   👉 [Unstop] Navigating...")
    # Unstop uses a query parameter
    url = f"https://unstop.com/internships?searchTerm={keyword}"
    
    try:
        await page.goto(url, timeout=60000)
        # Unstop is a Single Page App (SPA), needs time to load JS
        await page.wait_for_timeout(5000) 
        # Look for their specific card class
        await page.wait_for_selector("div.content", timeout=10000)
    except:
        print("   ⚠️ [Unstop] No internships found.")
        return 0

    # Unstop changes classes often, but 'app-job-card' or generic containers usually work
    # We look for any link that contains '/internships/' in the href
    job_links = await page.query_selector_all("a[href*='/internships/']")
    count = 0
    
    for link in job_links:
        try:
            href = await link.get_attribute("href")
            # Filter out generic links (like "View All")
            if len(href) < 30 or "search" in href: continue
            
            # Title is usually inside a strong or h2 tag inside the link
            title_el = await link.query_selector("strong") or await link.query_selector("h2") or await link.query_selector("h3")
            if not title_el: continue
            
            title = await title_el.inner_text()
            
            # Company is harder to find in the list view on Unstop
            # We will label it generically or try to find the neighbor div
            company = "Unstop Partner" 
            
            # Unstop links are usually full absolute URLs
            full_link = href if href.startswith("http") else f"https://unstop.com{href}"

            if save_job(db, title, company, full_link, "Unstop"):
                count += 1
        except:
            continue

    print(f"   ✅ [Unstop] Found {count} new internships.")
    return count

# ==========================================
# SITE 3: PROSPLE INDIA (Student Friendly)
# ==========================================
async def scrape_prosple(page, keyword, db):
    print(f"   👉 [Prosple] Navigating...")
    url = f"https://in.prosple.com/search-jobs?keywords={keyword}"
    
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_selector("div.SearchJobCard", timeout=15000)
    except:
        print("   ⚠️ [Prosple] No internships found.")
        return 0

    cards = await page.query_selector_all("div.SearchJobCard")
    count = 0

    for card in cards:
        try:
            title_el = await card.query_selector("h2")
            company_el = await card.query_selector("div.sc-gswNZR") # Prosple uses weird generated classes
            link_el = await card.query_selector("a")

            if not title_el or not link_el: continue

            title = await title_el.inner_text()
            # If company class is dynamic, we fallback
            company = await company_el.inner_text() if company_el else "Prosple Employer"
            
            relative_link = await link_el.get_attribute("href")
            full_link = f"https://in.prosple.com{relative_link}"

            if save_job(db, title, company, full_link, "Prosple India"):
                count += 1
        except:
            continue

    print(f"   ✅ [Prosple] Found {count} new internships.")
    return count

# ==========================================
# HELPER: SAVE TO DB
# ==========================================
def save_job(db, title, company, link, source):
    # Filter: Strict quality control
    if len(title) < 3 or len(link) < 10: return False

    # Deduplicate
    existing = db.query(models.Internship).filter(models.Internship.link == link).first()
    if not existing:
        new_job = models.Internship(
            title=title,
            company=company,
            link=link,
            source=source
        )
        db.add(new_job)
        print(f"      + [{source}] Added: {title}")
        return True
    return False

# ==========================================
# MAIN RUNNER
# ==========================================
async def scrape_internships(db: Session, keyword: str):
    print(f"🚀 [Scraper] Starting Indian Internship Search for: {keyword}")
    total_new_jobs = 0
    
    async with async_playwright() as p:
        print("🚀 [Scraper] Launching Browser...")
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        
        # Important: Viewport size helps with "Unstop" layout loading
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        # 1. Internshala
        total_new_jobs += await scrape_internshala(page, keyword, db)
        
        # 2. Unstop
        total_new_jobs += await scrape_unstop(page, keyword, db)

        # 3. Prosple
        total_new_jobs += await scrape_prosple(page, keyword, db)

        db.commit()
        await browser.close()
        
    print(f"🏁 [Scraper] Finished. Total new internships added: {total_new_jobs}")
    return {"status": "success", "new_jobs_count": total_new_jobs}