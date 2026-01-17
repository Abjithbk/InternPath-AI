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
    "--disable-blink-features=AutomationControlled", # Hides bot status
]

# --- 1. INTELLIGENT RELEVANCE FILTER ---
def is_relevant(title, keyword):
    """
    Returns True ONLY if the job title matches the user's search intent.
    """
    title_lower = title.lower()
    keyword_lower = keyword.lower()
    
    # Words to ignore when matching (too generic)
    ignore_words = ["intern", "internship", "job", "summer", "fresher", "part-time", "full-time", "remote"]
    search_terms = [w for w in keyword_lower.split() if w not in ignore_words]
    
    # Smart Expansion: If user searches "software", also accept "developer", "engineer"
    if "software" in keyword_lower:
        search_terms.extend(["developer", "engineer", "sde", "coding", "full stack", "backend", "frontend", "web", "app", "data"])
    elif "marketing" in keyword_lower:
        search_terms.extend(["sales", "brand", "business", "growth", "seo", "content", "social media"])
    
    # If no specific terms found, be lenient
    if not search_terms: 
        return True
        
    # Strict Check: Title MUST contain at least one search term
    for term in search_terms:
        if term in title_lower:
            return True
            
    return False

# --- 2. THE GOOGLE BACKUP (Failsafe) ---
async def scrape_via_google(context, site_name, site_domain, keyword, db):
    print(f"   🛡️ [Backup] Switching to Google Search for {site_name}...")
    page = await context.new_page()
    
    # Query: site:internshala.com "software intern"
    query = f"site:{site_domain} {keyword}"
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}&num=20&hl=en"
    
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_selector("div.g", timeout=10000)
    except:
        print(f"      ❌ [Backup] Google timed out for {site_name}.")
        await page.close()
        return 0

    results = await page.query_selector_all("div.g")
    count = 0
    
    for res in results:
        try:
            link_el = await res.query_selector("a")
            title_el = await res.query_selector("h3")
            
            if not link_el or not title_el: continue
            
            full_link = await link_el.get_attribute("href")
            title = await title_el.inner_text()
            
            # Strict Validation
            if site_domain not in full_link: continue
            if "login" in full_link or "signup" in full_link: continue
            if not is_relevant(title, keyword): continue # Filter irrelevant jobs

            clean_title = title.split("-")[0].split("|")[0].strip()
            
            if save_job(db, clean_title, f"{site_name} (via Google)", full_link, f"Google-{site_name}"):
                count += 1
        except: continue

    print(f"   ✅ [Backup] Found {count} jobs via Google.")
    await page.close()
    return count

# --- 3. INTERNSHALA (Direct Mobile) ---
async def scrape_internshala(context, keyword, db):
    print(f"   👉 [Internshala] Searching Direct...")
    page = await context.new_page()
    # Block heavy media for speed
    await page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_())

    fmt_keyword = keyword.replace(" ", "-")
    url = f"https://internshala.com/internships/keywords-{fmt_keyword}"
    
    try:
        await page.goto(url, timeout=45000)
        await page.wait_for_selector(".individual_internship", timeout=15000)
    except:
        print("      ⚠️ [Internshala] Direct Blocked/Timeout.")
        await page.close()
        return 0 # Trigger Backup

    cards = await page.query_selector_all(".individual_internship")
    count = 0
    for card in cards:
        try:
            if not await card.get_attribute("internshipid"): continue

            title_el = await card.query_selector("h3") or await card.query_selector(".profile")
            if not title_el: continue
            title = await title_el.inner_text()
            
            if not is_relevant(title, keyword): continue # Filter!

            company_el = await card.query_selector(".company_name")
            company = await company_el.inner_text() if company_el else "Internshala Employer"
            
            link_el = await card.query_selector(".view_detail_button") or await card.query_selector("a")
            if not link_el: continue
            
            full_link = f"https://internshala.com{await link_el.get_attribute('href')}"
            
            if save_job(db, title.strip(), company.strip(), full_link, "Internshala"):
                count += 1
        except: continue

    print(f"   ✅ [Internshala] Found {count} jobs.")
    await page.close()
    return count

# --- 4. UNSTOP (DuckDuckGo Proxy) ---
async def scrape_unstop(context, keyword, db):
    print(f"   👉 [Unstop] Searching via Proxy...")
    page = await context.new_page()
    
    # Use DDG to bypass Unstop's heavy cloudflare
    query = f"site:unstop.com {keyword} internship"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
    
    try:
        await page.goto(url, timeout=45000)
        await page.wait_for_selector(".result__a", timeout=15000)
    except:
        print("      ⚠️ [Unstop] Proxy Timeout.")
        await page.close()
        return 0 # Trigger Backup

    results = await page.query_selector_all(".result")
    count = 0
    for res in results:
        try:
            link_el = await res.query_selector(".result__a")
            if not link_el: continue
            
            full_link = await link_el.get_attribute("href")
            title = await link_el.inner_text()
            
            if "unstop.com" not in full_link or "login" in full_link: continue
            if not is_relevant(title, keyword): continue # Filter!

            clean_title = title.split("|")[0].split("-")[0].strip()
            
            if save_job(db, clean_title, "Unstop Partner", full_link, "Unstop"):
                count += 1
        except: continue

    print(f"   ✅ [Unstop] Found {count} jobs.")
    await page.close()
    return count

# --- 5. PROSPLE (Direct) ---
async def scrape_prosple(context, keyword, db):
    print(f"   👉 [Prosple] Searching Direct...")
    page = await context.new_page()
    url = f"https://in.prosple.com/search-jobs?keywords={keyword}&locations=India"
    
    try:
        await page.goto(url, timeout=45000)
        if "Security" in await page.title():
            await page.close()
            return 0 # Trigger Backup
        await page.wait_for_selector("div.SearchJobCard", timeout=15000)
    except:
        print("      ⚠️ [Prosple] Direct Blocked/Timeout.")
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
            if not is_relevant(title, keyword): continue # Filter!

            full_link = f"https://in.prosple.com{await link_el.get_attribute('href')}"
            
            if save_job(db, title.strip(), "Prosple Employer", full_link, "Prosple India"):
                count += 1
        except: continue

    print(f"   ✅ [Prosple] Found {count} jobs.")
    await page.close()
    return count

# --- 6. DB SAVER ---
def save_job(db, title, company, link, source):
    if len(title) < 2 or "http" not in link: return False
    try:
        existing = db.query(models.Internship).filter(models.Internship.link == link).first()
        if not existing:
            new_job = models.Internship(
                title=title[:200], company=company[:100], link=link, source=source
            )
            db.add(new_job)
            db.commit() # INSTANT SAVE
            db.refresh(new_job)
            print(f"      + Added: {title[:30]}...")
            return True
    except:
        db.rollback()
    return False

# --- 7. MAIN LOGIC (SMART FALLBACK) ---
async def scrape_internships(db: Session, keyword: str):
    print(f"🚀 [Scraper] Smart Search for: {keyword}")
    total = 0
    
    async with async_playwright() as p:
        # Use Pixel 5 Emulation (Best for avoiding blocks)
        pixel_5 = p.devices['Pixel 5']
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        
        context_mobile = await browser.new_context(**pixel_5, locale="en-IN", timezone_id="Asia/Kolkata")
        context_desktop = await browser.new_context() # For Google

        # --- A. INTERNSHALA ---
        count = await scrape_internshala(context_mobile, keyword, db)
        if count == 0: # If Direct failed, use Google Backup
            count += await scrape_via_google(context_desktop, "Internshala", "internshala.com", keyword, db)
        total += count
        await asyncio.sleep(1)

        # --- B. UNSTOP ---
        count = await scrape_unstop(context_desktop, keyword, db)
        if count == 0: # If Proxy failed, use Google Backup
            count += await scrape_via_google(context_desktop, "Unstop", "unstop.com", keyword, db)
        total += count
        await asyncio.sleep(1)

        # --- C. PROSPLE ---
        count = await scrape_prosple(context_mobile, keyword, db)
        if count == 0: # If Direct failed, use Google Backup
            count += await scrape_via_google(context_desktop, "Prosple", "in.prosple.com", keyword, db)
        total += count

        await browser.close()
        
    print(f"🏁 [Scraper] Finished. Total Saved: {total}")
    return {"status": "success", "count": total}