import asyncio
import random
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

# --- CONFIGURATION ---
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    "--window-size=1920,1080"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

# --- UTILS ---
async def block_aggressively(route):
    if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
        await route.abort()
    else:
        await route.continue_()

async def stealth_page(context):
    page = await context.new_page()
    await page.route("**/*", block_aggressively)
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
    return page

# ==========================================
# 1. INTERNSHALA
# ==========================================
async def scrape_internshala(context, keyword, db):
    print(f"   👉 [Internshala] Starting...")
    page = await stealth_page(context)
    fmt_keyword = keyword.replace(" ", "-")
    url = f"https://internshala.com/internships/keywords-{fmt_keyword}"
    
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_selector("#internship_list_container_1", timeout=20000)
    except Exception as e:
        print(f"      ⚠️ [Internshala] Error: {str(e)[:50]}")
        await page.close()
        return 0

    cards = await page.query_selector_all(".individual_internship")
    count = 0
    for card in cards:
        try:
            if not await card.get_attribute("internshipid"): continue

            title_el = await card.query_selector("h3") or await card.query_selector(".profile")
            link_el = await card.query_selector(".view_detail_button") or await card.query_selector("a")
            
            if not title_el or not link_el: continue
            
            title = await title_el.inner_text()
            company_el = await card.query_selector(".company_name")
            company = await company_el.inner_text() if company_el else "Internshala"
            
            rel_link = await link_el.get_attribute("href")
            full_link = f"https://internshala.com{rel_link}"
            
            if save_job(db, title.strip(), company.strip(), full_link, "Internshala"):
                count += 1
        except: continue

    print(f"   ✅ [Internshala] Saved {count} jobs.")
    await page.close()
    return count

# ==========================================
# 2. UNSTOP
# ==========================================
async def scrape_unstop(context, keyword, db):
    print(f"   👉 [Unstop] Starting...")
    page = await stealth_page(context)
    url = f"https://unstop.com/internships?searchTerm={keyword}"
    
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_selector("a[href*='/internships/']", timeout=20000)
    except Exception as e:
        print(f"      ⚠️ [Unstop] Error: {str(e)[:50]}")
        await page.close()
        return 0

    links = await page.query_selector_all("a[href*='/internships/']")
    count = 0
    for link in links:
        try:
            href = await link.get_attribute("href")
            if "search" in href or len(href) < 30: continue
            
            title_el = await link.query_selector("strong") or await link.query_selector("h2")
            if not title_el: continue

            title = await title_el.inner_text()
            full_link = href if href.startswith("http") else f"https://unstop.com{href}"
            
            if save_job(db, title.strip(), "Unstop Partner", full_link, "Unstop"):
                count += 1
        except: continue
        
    print(f"   ✅ [Unstop] Saved {count} jobs.")
    await page.close()
    return count

# ==========================================
# 3. PROSPLE
# ==========================================
async def scrape_prosple(context, keyword, db):
    print(f"   👉 [Prosple] Starting...")
    page = await stealth_page(context)
    url = f"https://in.prosple.com/search-jobs?keywords={keyword}&locations=India"
    
    try:
        await page.goto(url, timeout=60000)
        
        title = await page.title()
        if "Attention" in title or "Security" in title:
            print("      ⚠️ [Prosple] Blocked by Cloudflare.")
            await page.close()
            return 0
            
        await page.wait_for_selector("div.SearchJobCard", timeout=20000)
    except Exception as e:
        print(f"      ⚠️ [Prosple] Error: {str(e)[:50]}")
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
            rel_link = await link_el.get_attribute("href")
            full_link = f"https://in.prosple.com{rel_link}"
            
            if save_job(db, title.strip(), "Prosple Employer", full_link, "Prosple India"):
                count += 1
        except: continue

    print(f"   ✅ [Prosple] Saved {count} jobs.")
    await page.close()
    return count

# ==========================================
# HELPER: SAVE TO DB
# ==========================================
def save_job(db, title, company, link, source):
    if len(title) < 2 or "http" not in link: return False
    try:
        existing = db.query(models.Internship).filter(models.Internship.link == link).first()
        if not existing:
            new_job = models.Internship(title=title[:200], company=company[:100], link=link, source=source)
            db.add(new_job)
            db.commit() # Save Immediately
            db.refresh(new_job)
            print(f"      + Added: {title[:30]}...")
            return True
    except:
        db.rollback()
    return False

# ==========================================
# MAIN RUNNER
# ==========================================
async def scrape_internships(db: Session, keyword: str):
    print(f"🚀 [Scraper] Starting Search for: {keyword}")
    total = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080},
            locale="en-IN",
            timezone_id="Asia/Kolkata"
        )

        # Run Sequentially (Safer for Render Free Tier)
        total += await scrape_internshala(context, keyword, db)
        await asyncio.sleep(1)
        total += await scrape_unstop(context, keyword, db)
        await asyncio.sleep(1)
        total += await scrape_prosple(context, keyword, db)

        await browser.close()
        
    print(f"🏁 [Scraper] Finished. Total Saved: {total}")
    return {"status": "success", "count": total}