import asyncio
import random
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

# --- STEALTH CONFIGURATION ---
# These arguments hide the fact that we are a bot
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled", # <--- CRITICAL: Hides 'navigator.webdriver'
    "--window-size=1920,1080"
]

# Real User Agents (Rotated to avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

async def stealth_page(context):
    """Creates a page with anti-bot scripts injected."""
    page = await context.new_page()
    # Mask the webdriver property
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    return page

# ==========================================
# 1. INTERNSHALA (Direct Scrape)
# ==========================================
async def scrape_internshala(context, keyword, db):
    print(f"   👉 [Internshala] Direct search for '{keyword}'...")
    page = await stealth_page(context)
    
    # URL Format: internshala.com/internships/keywords-python
    fmt_keyword = keyword.replace(" ", "-")
    url = f"https://internshala.com/internships/keywords-{fmt_keyword}"
    
    try:
        await page.goto(url, timeout=60000)
        # Random mouse movements to look human
        await page.mouse.move(100, 200)
        await page.mouse.move(300, 400)
        
        # Wait for list or "no results"
        try:
            await page.wait_for_selector("#internship_list_container_1", timeout=15000)
        except:
            print("      ⚠️ Internshala: List container not found.")
            await page.close()
            return 0
    except:
        await page.close()
        return 0

    # Scrape Cards
    cards = await page.query_selector_all(".individual_internship")
    count = 0
    
    for card in cards:
        try:
            # Check for ID to skip ads
            iid = await card.get_attribute("internshipid")
            if not iid: continue

            title_el = await card.query_selector(".profile") or await card.query_selector("h3")
            company_el = await card.query_selector(".company_name") or await card.query_selector(".link_display_like_text")
            link_el = await card.query_selector(".view_detail_button") or await card.query_selector("a")

            if not title_el: continue
            
            title = await title_el.inner_text()
            company = await company_el.inner_text() if company_el else "Internshala Employer"
            
            relative_link = await link_el.get_attribute("href")
            full_link = f"https://internshala.com{relative_link}"
            
            if save_job(db, title.strip(), company.strip(), full_link, "Internshala"):
                count += 1
        except: continue

    print(f"   ✅ [Internshala] Found {count} internships.")
    await page.close()
    return count

# ==========================================
# 2. UNSTOP (Direct Scrape)
# ==========================================
async def scrape_unstop(context, keyword, db):
    print(f"   👉 [Unstop] Direct search for '{keyword}'...")
    page = await stealth_page(context)
    url = f"https://unstop.com/internships?searchTerm={keyword}"
    
    try:
        await page.goto(url, timeout=60000)
        # Unstop is heavy JS. Wait for network to be idle (finished loading)
        await page.wait_for_load_state("networkidle", timeout=10000)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    except:
        print("      ⚠️ Unstop: Timeout.")
        await page.close()
        return 0

    # Unstop links always contain '/internships/' in the href
    links = await page.query_selector_all("a[href*='/internships/']")
    count = 0
    
    for link in links:
        try:
            href = await link.get_attribute("href")
            # Filter garbage
            if "login" in href or "search" in href or len(href) < 30: continue
            
            # Title is usually generic in the list, we extract what we can
            title_el = await link.query_selector("strong") or await link.query_selector("h2")
            if not title_el: continue

            title = await title_el.inner_text()
            full_link = href if href.startswith("http") else f"https://unstop.com{href}"
            
            if save_job(db, title.strip(), "Unstop Partner", full_link, "Unstop"):
                count += 1
        except: continue
        
    print(f"   ✅ [Unstop] Found {count} internships.")
    await page.close()
    return count

# ==========================================
# 3. PROSPLE (Direct Scrape)
# ==========================================
async def scrape_prosple(context, keyword, db):
    print(f"   👉 [Prosple] Direct search for '{keyword}'...")
    page = await stealth_page(context)
    url = f"https://in.prosple.com/search-jobs?keywords={keyword}&locations=India"
    
    try:
        await page.goto(url, timeout=60000)
        # Check for Cloudflare/Access Denied
        title = await page.title()
        if "Attention" in title or "Security" in title:
            print("      ⚠️ Prosple blocked us (Cloudflare).")
            await page.close()
            return 0
        
        await page.wait_for_selector("div.SearchJobCard", timeout=15000)
    except:
        await page.close()
        return 0

    cards = await page.query_selector_all("div.SearchJobCard")
    count = 0
    
    for card in cards:
        try:
            title_el = await card.query_selector("h2")
            link_el = await card.query_selector("a")
            if not title_el or not link_el: continue

            title = await title_el.inner_text()
            relative_link = await link_el.get_attribute("href")
            full_link = f"https://in.prosple.com{relative_link}"
            
            if save_job(db, title.strip(), "Prosple Employer", full_link, "Prosple India"):
                count += 1
        except: continue

    print(f"   ✅ [Prosple] Found {count} internships.")
    await page.close()
    return count

# ==========================================
# HELPER: SAVE TO DB
# ==========================================
def save_job(db, title, company, link, source):
    # Validation
    if len(title) < 2 or "http" not in link: return False
    
    # Deduplicate
    existing = db.query(models.Internship).filter(models.Internship.link == link).first()
    if not existing:
        new_job = models.Internship(
            title=title[:200], 
            company=company[:100],
            link=link,
            source=source
        )
        db.add(new_job)
        print(f"      + Added: {title[:30]}...")
        return True
    return False

# ==========================================
# MAIN RUNNER
# ==========================================
async def scrape_internships(db: Session, keyword: str):
    print(f"🚀 [Scraper] Starting STEALTH Direct Mode: {keyword}")
    total = 0
    
    async with async_playwright() as p:
        print("🚀 [Scraper] Launching Browser (Stealth Mode)...")
        
        # Launch browser
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        
        # Create Context with Real User Agent
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080},
            locale="en-IN", # Look like a user from India
            timezone_id="Asia/Kolkata"
        )

        # 1. Internshala
        total += await scrape_internshala(context, keyword, db)
        
        # 2. Unstop
        total += await scrape_unstop(context, keyword, db)

        # 3. Prosple
        total += await scrape_prosple(context, keyword, db)

        db.commit()
        await browser.close()
        
    print(f"🏁 [Scraper] Finished. Total: {total}")
    return {"status": "success", "count": total}