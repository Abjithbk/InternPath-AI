import asyncio
import random
import urllib.parse
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
]

# --- INTELLIGENT FILTERING ---
def is_relevant(title, keyword):
    """
    Returns True only if the job title matches the user's intent.
    """
    title_lower = title.lower()
    keyword_lower = keyword.lower()
    
    ignore_words = ["intern", "internship", "job", "summer", "fresher", "part-time", "full-time"]
    search_terms = [w for w in keyword_lower.split() if w not in ignore_words]
    
    # Keyword Expansion
    if "software" in keyword_lower:
        search_terms.extend(["developer", "engineer", "sde", "coding", "web", "app", "data", "backend", "frontend", "fullstack"])
    elif "marketing" in keyword_lower:
        search_terms.extend(["sales", "brand", "business", "growth", "seo", "content"])
    
    if not search_terms: 
        return True
        
    for term in search_terms:
        if term in title_lower:
            return True
    return False

# ==========================================
# 1. INTERNSHALA (Mobile Mode)
# ==========================================
async def scrape_internshala(context, keyword, db):
    print(f"   👉 [Internshala] Searching '{keyword}'...")
    page = await context.new_page()
    await page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_())

    fmt_keyword = keyword.replace(" ", "-")
    url = f"https://internshala.com/internships/keywords-{fmt_keyword}"
    
    try:
        await page.goto(url, timeout=45000)
        await page.mouse.wheel(0, 1000)
        await page.wait_for_selector(".individual_internship", timeout=15000)
    except:
        print("      ⚠️ [Internshala] Timeout or Blocked.")
        await page.close()
        return 0

    cards = await page.query_selector_all(".individual_internship")
    count = 0
    
    for card in cards:
        try:
            if not await card.get_attribute("internshipid"): continue

            title_el = await card.query_selector("h3") or await card.query_selector(".profile")
            if not title_el: continue
            title = await title_el.inner_text()
            
            if not is_relevant(title, keyword): continue

            company_el = await card.query_selector(".company_name")
            company = await company_el.inner_text() if company_el else "Internshala Employer"
            
            link_el = await card.query_selector(".view_detail_button") or await card.query_selector("a")
            if not link_el: continue
            
            full_link = f"https://internshala.com{await link_el.get_attribute('href')}"
            
            if save_job(db, title.strip(), company.strip(), full_link, "Internshala"):
                count += 1
        except: continue

    print(f"   ✅ [Internshala] Found {count} relevant jobs.")
    await page.close()
    return count

# ==========================================
# 2. UNSTOP (DuckDuckGo Proxy)
# ==========================================
async def scrape_unstop_via_proxy(context, keyword, db):
    print(f"   👉 [Unstop] Searching via Proxy...")
    page = await context.new_page()
    
    query = f"site:unstop.com {keyword} internship"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
    
    try:
        await page.goto(url, timeout=45000)
        await page.wait_for_selector(".result__a", timeout=15000)
    except:
        print("      ⚠️ [Unstop Proxy] Timeout.")
        await page.close()
        return 0

    results = await page.query_selector_all(".result")
    count = 0
    
    for res in results:
        try:
            link_el = await res.query_selector(".result__a")
            if not link_el: continue
            
            full_link = await link_el.get_attribute("href")
            title = await link_el.inner_text()
            
            if "unstop.com" not in full_link or "login" in full_link: continue
            if not is_relevant(title, keyword): continue

            clean_title = title.split("|")[0].split("-")[0].strip()
            
            if save_job(db, clean_title, "Unstop Partner", full_link, "Unstop (Proxy)"):
                count += 1
        except: continue

    print(f"   ✅ [Unstop] Found {count} relevant jobs.")
    await page.close()
    return count

# ==========================================
# 3. PROSPLE (Direct Mode)
# ==========================================
async def scrape_prosple(context, keyword, db):
    print(f"   👉 [Prosple] Searching '{keyword}'...")
    page = await context.new_page()
    url = f"https://in.prosple.com/search-jobs?keywords={keyword}&locations=India"
    
    try:
        await page.goto(url, timeout=45000)
        # Check security
        title = await page.title()
        if "Attention" in title or "Security" in title:
            print("      ⚠️ [Prosple] Blocked.")
            await page.close()
            return 0
        await page.wait_for_selector("div.SearchJobCard", timeout=15000)
    except:
        print("      ⚠️ [Prosple] Timeout or no results.")
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
            if not is_relevant(title, keyword): continue

            full_link = f"https://in.prosple.com{await link_el.get_attribute('href')}"
            
            if save_job(db, title.strip(), "Prosple Employer", full_link, "Prosple India"):
                count += 1
        except: continue

    print(f"   ✅ [Prosple] Found {count} relevant jobs.")
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
            new_job = models.Internship(
                title=title[:200], company=company[:100], link=link, source=source
            )
            db.add(new_job)
            db.commit() 
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
    print(f"🚀 [Scraper] Starting All-Source Search: {keyword}")
    total = 0
    
    async with async_playwright() as p:
        # Use Pixel 5 emulation for best compatibility
        pixel_5 = p.devices['Pixel 5']
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        
        # Contexts
        context_mobile = await browser.new_context(**pixel_5, locale="en-IN", timezone_id="Asia/Kolkata")
        context_desktop = await browser.new_context()

        # Run Sequentially (Safer for Render Free Tier)
        total += await scrape_internshala(context_mobile, keyword, db)
        await asyncio.sleep(1)
        total += await scrape_unstop_via_proxy(context_desktop, keyword, db)
        await asyncio.sleep(1)
        total += await scrape_prosple(context_mobile, keyword, db) # Mobile context works well for Prosple too

        await browser.close()
        
    print(f"🏁 [Scraper] Finished. Total Relevant Jobs: {total}")
    return {"status": "success", "count": total}