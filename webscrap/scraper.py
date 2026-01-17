import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from . import models

# --- CONFIGURATION ---
BROWSER_ARGS = ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]

# --- HELPER: DATE PARSER ---
def parse_date(date_str):
    """Converts '15 Jan 25' to SQL Date object."""
    if not date_str: return None
    text = date_str.lower().strip()
    if "immediate" in text or "start" in text: return None
    
    formats = ["%d %b'%y", "%d %b %y", "%d-%m-%Y", "%Y-%m-%d"]
    clean_text = text.replace("'", "").replace(",", "")
    
    for fmt in formats:
        try:
            return datetime.strptime(clean_text, fmt).date()
        except: continue
    return None

# --- HELPER: SAVE TO DB ---
def save_job(db, data, keyword):
    if len(data['title']) < 2: return False
    
    # Check Duplicate
    exists = db.query(models.Internship).filter(models.Internship.link == data['link']).first()
    if exists: return False

    try:
        new_job = models.Internship(
            title=data['title'], company=data['company'], link=data['link'], 
            source=data['source'], keyword=keyword,
            location=data['location'], duration=data['duration'], 
            stipend=data['stipend'], skills=data['skills'],
            apply_by=parse_date(data['apply_by'])
        )
        db.add(new_job)
        db.commit()
        return True
    except:
        db.rollback()
        return False

# --- 1. INTERNSHALA ---
async def scrape_internshala(keyword, db, limit=20):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        # Pixel 5 for Mobile View (Often simpler HTML)
        context = await browser.new_context(**p.devices['Pixel 5']) 
        page = await context.new_page()

        try:
            fmt_keyword = keyword.replace(" ", "-")
            await page.goto(f"https://internshala.com/internships/keywords-{fmt_keyword}", timeout=60000)
            await page.wait_for_selector(".individual_internship", timeout=15000)
        except:
            await browser.close()
            return 0

        cards = await page.query_selector_all(".individual_internship")
        count = 0
        for card in cards:
            if count >= limit: break
            try:
                if not await card.get_attribute("internshipid"): continue
                
                title = await (await card.query_selector("h3")).inner_text()
                link = f"https://internshala.com{await (await card.query_selector('.view_detail_button')).get_attribute('href')}"
                company = await (await card.query_selector(".company_name")).inner_text()
                
                # Extract Details from rows
                items = await card.query_selector_all(".item_body")
                duration = await items[1].inner_text() if len(items) > 1 else "N/A"
                stipend = await items[2].inner_text() if len(items) > 2 else "Unpaid"
                
                job_data = {
                    "title": title.strip(), "company": company.strip(), "link": link,
                    "source": "Internshala", "location": "Remote/Hybrid", 
                    "duration": duration, "stipend": stipend, 
                    "skills": "See Details", "apply_by": "15 Jan 25" # Placeholder as this varies
                }
                if save_job(db, job_data, keyword): count += 1
            except: continue
        
        await browser.close()
        return count

# --- 2. UNSTOP ---
async def scrape_unstop(keyword, db, limit=20):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        page = await browser.new_page()
        
        try:
            await page.goto(f"https://unstop.com/internships?searchTerm={keyword}", timeout=60000)
            await page.wait_for_selector("a[href*='/internships/']", timeout=15000)
        except:
            await browser.close()
            return 0

        links = await page.query_selector_all("a[href*='/internships/']")
        count = 0
        for link in links:
            if count >= limit: break
            try:
                title_el = await link.query_selector("h2") or await link.query_selector("strong")
                if not title_el: continue
                title = await title_el.inner_text()
                
                href = await link.get_attribute("href")
                full_link = href if href.startswith("http") else f"https://unstop.com{href}"
                
                # Unstop details are often hidden in list view, basic extraction:
                job_data = {
                    "title": title.strip(), "company": "Unstop Partner", "link": full_link,
                    "source": "Unstop", "location": "India", 
                    "duration": "N/A", "stipend": "See Link", 
                    "skills": "See Link", "apply_by": None
                }
                if save_job(db, job_data, keyword): count += 1
            except: continue

        await browser.close()
        return count

# --- 3. PROSPLE ---
async def scrape_prosple(keyword, db, limit=20):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        page = await browser.new_page()
        
        try:
            await page.goto(f"https://in.prosple.com/search-jobs?keywords={keyword}", timeout=60000)
            await page.wait_for_selector("div.SearchJobCard", timeout=15000)
        except:
            await browser.close()
            return 0

        cards = await page.query_selector_all("div.SearchJobCard")
        count = 0
        for card in cards:
            if count >= limit: break
            try:
                title = await (await card.query_selector("h2")).inner_text()
                href = await (await card.query_selector("a")).get_attribute("href")
                full_link = f"https://in.prosple.com{href}"
                
                stipend_el = await card.query_selector(".SearchJobCard__salary")
                stipend = await stipend_el.inner_text() if stipend_el else "Hidden"

                job_data = {
                    "title": title.strip(), "company": "Prosple Employer", "link": full_link,
                    "source": "Prosple", "location": "India", 
                    "duration": "N/A", "stipend": stipend, 
                    "skills": "N/A", "apply_by": None
                }
                if save_job(db, job_data, keyword): count += 1
            except: continue

        await browser.close()
        return count