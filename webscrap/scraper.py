import asyncio
import random
import gc
from datetime import date, timedelta
from patchright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

# --- CONFIG ---
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--window-position=0,0",
    "--ignore-certificate-errors",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
]

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

def get_fallback_date():
    return date.today() + timedelta(days=14)

def save_job(db: Session, data: dict, keyword: str):
    if len(data['title']) < 2: return False
    exists = db.query(models.Internship).filter(models.Internship.link == data['link']).first()
    if exists: return False

    try:
        apply_by = data.get('apply_by')
        if not apply_by: apply_by = get_fallback_date()

        new_job = models.Internship(
            title=data['title'][:200], company=data['company'][:100], link=data['link'],
            source=data['source'], keyword=keyword,
            location=data.get('location', 'Remote')[:100],
            duration=data.get('duration', 'N/A')[:50], stipend=data.get('stipend', 'N/A')[:100],
            skills=data.get('skills', 'N/A')[:200], apply_by=apply_by
        )
        db.add(new_job)
        db.commit()
        return True
    except Exception as e:
        print(f"❌ [DB Error] Could not save job: {e}")
        db.rollback()
        return False

async def create_stealth_page(context):
    page = await context.new_page()
    await page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font", "stylesheet"] else r.continue_())
    return page

# --- SCRAPERS ---

async def scrape_internshala(keyword: str, db: Session, limit: int = 20):
    print(f"   👉 [Internshala] Searching '{keyword}'...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={'width': 1280, 'height': 720})
        page = await create_stealth_page(context)

        try:
            url = f"https://internshala.com/internships/keywords-{keyword.replace(' ', '-')}"
            # Internshala is fast, 'load' is fine
            await page.goto(url, timeout=45000)
            await page.wait_for_selector(".individual_internship", timeout=15000)
        except Exception as e:
            print(f"   ❌ [Internshala] Load Failed: {e}")
            await browser.close(); return 0

        cards = await page.query_selector_all(".individual_internship")
        count = 0
        for card in cards:
            if count >= limit: break
            try:
                title_el = await card.query_selector("h3.job-internship-name") or await card.query_selector("h3")
                if not title_el: continue
                title = await title_el.inner_text()
                if not is_relevant(title, keyword): continue

                href = await card.get_attribute("data-href")
                if not href:
                    link_el = await card.query_selector(".view_detail_button") or await card.query_selector("a")
                    if link_el: href = await link_el.get_attribute("href")
                if not href: continue
                link = f"https://internshala.com{href}"

                company_el = await card.query_selector(".company_name") or await card.query_selector("p.company-name")
                company = await company_el.inner_text() if company_el else "Unknown"

                items = await card.query_selector_all(".item_body")
                duration = await items[1].inner_text() if len(items) > 1 else "N/A"
                stipend = await items[2].inner_text() if len(items) > 2 else "Unpaid"
                
                job_data = {"title": title.strip(), "company": company.strip(), "link": link, "source": "Internshala", "location": "Remote/Hybrid", "duration": duration, "stipend": stipend, "skills": "See Details", "apply_by": None}
                if save_job(db, job_data, keyword): count += 1
            except: continue
        
        print(f"   ✅ [Internshala] Saved {count} jobs.")
        await browser.close()
        gc.collect()
        return count

async def scrape_unstop(keyword: str, db: Session, limit: int = 20):
    print(f"   👉 [Unstop] Searching '{keyword}'...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={'width': 1280, 'height': 720})
        page = await create_stealth_page(context)
        try:
            # Wait for DOMContentLoaded (Faster)
            await page.goto(f"https://unstop.com/internships?searchTerm={keyword}", timeout=45000, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000) # Give JS time to render cards
        except:
            await browser.close(); return 0

        # Try multiple selectors for cards
        links = await page.query_selector_all("a[href*='/internships/']")
        if not links:
            links = await page.query_selector_all("div.opportunity-card a") # Fallback selector
            
        count = 0
        for link in links:
            if count >= limit: break
            try:
                title_el = await link.query_selector("strong") or await link.query_selector("h2")
                if not title_el: continue
                title = await title_el.inner_text()
                if not is_relevant(title, keyword): continue
                
                href = await link.get_attribute("href")
                if not href: continue
                full_link = href if href.startswith("http") else f"https://unstop.com{href}"
                
                job_data = {"title": title.strip(), "company": "Unstop Partner", "link": full_link, "source": "Unstop", "location": "India", "duration": "N/A", "stipend": "See Link", "skills": "See Link", "apply_by": None}
                if save_job(db, job_data, keyword): count += 1
            except: continue
        
        print(f"   ✅ [Unstop] Saved {count} jobs.")
        await browser.close()
        gc.collect()
        return count

async def scrape_prosple(keyword: str, db: Session, limit: int = 20):
    print(f"   👉 [Prosple] Searching '{keyword}'...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={'width': 1280, 'height': 720})
        page = await create_stealth_page(context)
        try:
            # FIX: Use 'domcontentloaded' to avoid Timeouts on slow networks
            await page.goto(f"https://in.prosple.com/search-jobs?keywords={keyword}&locations=India", timeout=45000, wait_until="domcontentloaded")
            
            if "Security" in await page.title(): 
                await browser.close(); return 0
            
            await page.wait_for_timeout(3000) # Short nap for hydration
            await page.wait_for_selector("div.SearchJobCard", timeout=10000)
        except:
            await browser.close(); return 0

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
                job_data = {"title": title.strip(), "company": "Prosple Employer", "link": full_link, "source": "Prosple", "location": "India", "duration": "N/A", "stipend": stipend, "skills": "N/A", "apply_by": None}
                if save_job(db, job_data, keyword): count += 1
            except: continue
        
        print(f"   ✅ [Prosple] Saved {count} jobs.")
        await browser.close()
        gc.collect()
        return count