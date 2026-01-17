import asyncio
import random
from playwright.async_api import async_playwright
from datetime import date, timedelta
from . import models

# --- STEALTH CONFIGURATION ---
# 1. Hide Bot Status
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled", # <--- CRITICAL
    "--disable-infobars",
    "--window-position=0,0",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors",
]

# 2. Mimic Real Phones
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
]

# --- RELEVANCE FILTER ---
def is_relevant(title, keyword):
    title_lower = title.lower()
    keyword_lower = keyword.lower()
    
    ignore_words = ["intern", "internship", "job", "summer", "fresher", "part-time", "full-time", "remote"]
    search_terms = [w for w in keyword_lower.split() if w not in ignore_words]
    
    if "software" in keyword_lower:
        search_terms.extend(["developer", "engineer", "sde", "coding", "full stack", "backend", "web", "data"])
    elif "marketing" in keyword_lower:
        search_terms.extend(["sales", "brand", "business", "growth", "seo", "content"])
    
    if not search_terms: return True
    for term in search_terms:
        if term in title_lower: return True
    return False

# --- STEALTH PAGE CREATOR ---
async def create_stealth_page(context):
    page = await context.new_page()
    # Delete 'navigator.webdriver' flag
    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    # Block images to speed up loading
    await page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_())
    return page

# --- 1. INTERNSHALA ---
async def scrape_internshala(keyword, db, limit=20):
    print(f"   👉 [Internshala] Stealth Search for '{keyword}'...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={'width': 390, 'height': 844})
        page = await create_stealth_page(context)

        try:
            url = f"https://internshala.com/internships/keywords-{keyword.replace(' ', '-')}"
            await page.goto(url, timeout=45000)
            await page.wait_for_selector(".individual_internship", timeout=15000)
        except:
            print("      ⚠️ [Internshala] Timeout/Blocked.")
            await browser.close()
            return 0

        cards = await page.query_selector_all(".individual_internship")
        count = 0
        for card in cards:
            if count >= limit: break
            try:
                if not await card.get_attribute("internshipid"): continue
                title_el = await card.query_selector("h3")
                if not title_el: continue
                title = await title_el.inner_text()
                
                if not is_relevant(title, keyword): continue

                link = f"https://internshala.com{await (await card.query_selector('.view_detail_button')).get_attribute('href')}"
                company = await (await card.query_selector(".company_name")).inner_text()
                
                items = await card.query_selector_all(".item_body")
                duration = await items[1].inner_text() if len(items) > 1 else "N/A"
                stipend = await items[2].inner_text() if len(items) > 2 else "Unpaid"
                
                job_data = {
                    "title": title.strip(), "company": company.strip(), "link": link,
                    "source": "Internshala", "location": "Remote/Hybrid", 
                    "duration": duration, "stipend": stipend, 
                    "skills": "See Details", "apply_by": "15 Jan 25"
                }
                if save_job(db, job_data, keyword): count += 1
            except: continue
        
        await browser.close()
        return count

# --- 2. UNSTOP ---
async def scrape_unstop(keyword, db, limit=20):
    print(f"   👉 [Unstop] Stealth Search for '{keyword}'...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={'width': 390, 'height': 844})
        page = await create_stealth_page(context)
        
        try:
            await page.goto(f"https://unstop.com/internships?searchTerm={keyword}", timeout=60000)
            await page.wait_for_selector("a[href*='/internships/']", timeout=20000)
        except:
            print("      ⚠️ [Unstop] Timeout/Blocked.")
            await browser.close()
            return 0

        links = await page.query_selector_all("a[href*='/internships/']")
        count = 0
        for link in links:
            if count >= limit: break
            try:
                title_el = await link.query_selector("strong") or await link.query_selector("h2")
                if not title_el: continue
                title = await title_el.inner_text()
                if not is_relevant(title, keyword): continue

                href = await link.get_attribute("href")
                full_link = href if href.startswith("http") else f"https://unstop.com{href}"

                job_data = {
                    "title": title.strip(), "company": "Unstop Partner", "link": full_link,
                    "source": "Unstop", "location": "India", "duration": "N/A", 
                    "stipend": "See Link", "skills": "See Link", "apply_by": None
                }
                if save_job(db, job_data, keyword): count += 1
            except: continue
        await browser.close()
        return count

# --- 3. PROSPLE ---
async def scrape_prosple(keyword, db, limit=20):
    print(f"   👉 [Prosple] Stealth Search for '{keyword}'...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={'width': 390, 'height': 844})
        page = await create_stealth_page(context)
        
        try:
            await page.goto(f"https://in.prosple.com/search-jobs?keywords={keyword}&locations=India", timeout=60000)
            if "Security" in await page.title():
                print("      ⚠️ [Prosple] Cloudflare Blocked.")
                await browser.close()
                return 0
            await page.wait_for_selector("div.SearchJobCard", timeout=20000)
        except:
            print("      ⚠️ [Prosple] Timeout/Blocked.")
            await browser.close()
            return 0

        cards = await page.query_selector_all("div.SearchJobCard")
        count = 0
        for card in cards:
            if count >= limit: break
            try:
                title_el = await card.query_selector("h2")
                link_el = await card.query_selector("a")
                if not title_el or not link_el: continue
                title = await title_el.inner_text()
                if not is_relevant(title, keyword): continue

                full_link = f"https://in.prosple.com{await link_el.get_attribute('href')}"
                stipend_el = await card.query_selector(".SearchJobCard__salary")
                stipend = await stipend_el.inner_text() if stipend_el else "Hidden"

                job_data = {
                    "title": title.strip(), "company": "Prosple Employer", "link": full_link,
                    "source": "Prosple", "location": "India", "duration": "N/A", 
                    "stipend": stipend, "skills": "N/A", "apply_by": None
                }
                if save_job(db, job_data, keyword): count += 1
            except: continue
        await browser.close()
        return count

# --- DB SAVER (14-Day Fallback) ---
def save_job(db, data, keyword):
    if len(data['title']) < 2: return False
    exists = db.query(models.Internship).filter(models.Internship.link == data['link']).first()
    if exists: return False
    
    # Logic: If no date, expire in 14 days
    apply_by = date.today() + timedelta(days=14)
    
    try:
        new_job = models.Internship(
            title=data['title'], company=data['company'], link=data['link'], 
            source=data['source'], keyword=keyword, location=data['location'], 
            duration=data['duration'], stipend=data['stipend'], skills=data['skills'],
            apply_by=apply_by
        )
        db.add(new_job)
        db.commit()
        return True
    except:
        db.rollback()
        return False