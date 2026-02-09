import asyncio
import random
import gc
import re
from datetime import date, timedelta, datetime
from patchright.async_api import async_playwright
from sqlalchemy.orm import Session
from database import models

# --- CONFIGURATION ---
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-gl-drawing-for-tests",
    "--disable-gpu",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
]

def get_fallback_date():
    return date.today() + timedelta(days=14)

def parse_internshala_date(date_str):
    if not date_str: return get_fallback_date()
    text = date_str.lower().strip()
    if "immediate" in text: return date.today()
    try:
        clean = text.replace("apply by", "").replace("'", "").strip()
        return datetime.strptime(clean, "%d %b %y").date()
    except:
        return get_fallback_date()

def save_job(db: Session, data: dict, keyword: str):
    if len(data['title']) < 2: return False
    
    existing = db.query(models.Internship).filter(models.Internship.link == data['link']).first()
    
    if existing:
        updated = False
        if data['skills'] not in ["N/A", "Loading..."] and len(data['skills']) > 3:
            if existing.skills == "N/A" or len(existing.skills) < 5:
                existing.skills = data['skills'][:200]
                updated = True
        if data['apply_by'] and existing.apply_by != data['apply_by']:
            existing.apply_by = data['apply_by']
            updated = True
        if updated: db.commit()
        return False

    try:
        new_job = models.Internship(
            title=data['title'][:200], company=data['company'][:100], link=data['link'],
            source=data['source'], keyword=keyword,
            location=data.get('location', 'Remote')[:100],
            duration=data.get('duration', 'Flexible')[:50], 
            stipend=data.get('stipend', 'Unpaid')[:100],
            skills=data.get('skills', 'N/A')[:200], 
            apply_by=data.get('apply_by')
        )
        db.add(new_job)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False

async def create_stealth_page(context):
    page = await context.new_page()
    await page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font", "stylesheet"] else r.continue_())
    return page

def is_software_job(title: str, keyword: str) -> bool:
    t = title.lower()
    k = keyword.lower()
    block_keywords = ["marketing", "sales", "content", "hr", "business", "social media", "video", "graphic", "operations", "campus"]
    if any(bad in t for bad in block_keywords): return False
    if k in t: return True
    tech_keywords = ["software", "developer", "engineer", "web", "data", "ai", "app", "mobile", "tech", "stack", "full stack", "backend", "frontend"]
    if any(tech in t for tech in tech_keywords): return True
    return False

# --- DEEP SCRAPER (Date Only) ---
async def fetch_details(context, link):
    page = await create_stealth_page(context)
    apply_date = None
    backup_skills = None
    try:
        await page.goto(link, timeout=15000)
        content = await page.inner_text("body")
        
        m_date = re.search(r"Apply by(\s?\d{1,2}\s[A-Za-z]{3}'\s?\d{2})", content, re.IGNORECASE)
        if m_date: apply_date = parse_internshala_date(m_date.group(1))

        m_skills = re.search(r"Skills required(.*?)(?:Who can apply|Perks|Salary)", content, re.DOTALL | re.IGNORECASE)
        if m_skills:
             raw = m_skills.group(1).replace("\n", ",").strip()
             backup_skills = ", ".join([s.strip() for s in raw.split(",") if len(s.strip()) > 1])
    except:
        pass
    finally:
        await page.close()
    return backup_skills, apply_date

# --- MAIN SCRAPER ---
async def scrape_internshala(db: Session, limit: int = 15):
    # Predefined keywords — no user input
    keywords = ["python","web development","data science","node.js"]
    total_saved = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))

        for keyword in keywords:
            clean_term = " ".join([w for w in keyword.lower().split() if w not in ["internship", "job", "intern"]]).strip() or keyword
            print(f"   👉 [Internshala] Searching '{clean_term}'...")

            page = await create_stealth_page(context)

            try:
                url = f"https://internshala.com/internships/keywords-{clean_term.replace(' ', '-')}"
                await page.goto(url, timeout=45000)
                await page.wait_for_selector(".individual_internship", timeout=15000)
                cards = await page.query_selector_all(".individual_internship")
            except:
                await page.close()
                continue  # skip this keyword if page fails

            jobs_to_process = []
            count = 0

            for card in cards:
                if count >= limit:
                    break
                try:
                    title_el = await card.query_selector("h3")
                    if not title_el:
                        continue
                    title = await title_el.inner_text()
                    if not is_software_job(title, clean_term):
                        continue

                    href = await card.get_attribute("data-href")
                    if not href:
                        link_el = await card.query_selector(".view_detail_button") or await card.query_selector("a")
                        if link_el:
                            href = await link_el.get_attribute("href")
                    if not href:
                        continue
                    link = f"https://internshala.com{href}"

                    full_text = await card.inner_text()
                    stipend_match = re.search(r"(₹\s?[\d,]+(\s?-\s?[\d,]+)?(?:\s?/\s?\w+)?|Unpaid|Performance Based)", full_text, re.IGNORECASE)
                    stipend = stipend_match.group(0).strip() if stipend_match else "Hidden"

                    duration_match = re.search(r"(\d+\s?(?:Month|Week)s?)", full_text, re.IGNORECASE)
                    duration = duration_match.group(0).strip() if duration_match else "Flexible"

                    company_el = await card.query_selector(".company_name")
                    company = await company_el.inner_text() if company_el else "Unknown"

                    skills = "N/A"
                    skills_el = await card.query_selector(".job_skills") or await card.query_selector(".tags_container")
                    if skills_el:
                        raw_skills = await skills_el.inner_text()
                        skills = ", ".join([s.strip() for s in raw_skills.replace("\n", ",").split(',') if s.strip()])

                    # --- Clean Data ---
                    def clean_text(text, max_len=200):
                        if not text:
                            return None
                        return re.sub(r'\s+', ' ', text).strip().lower()[:max_len]
                    
                    def clean_company_name(company:str,max_len = 100):
                        if not company:
                            return "unknown"

                        # remove junk labels
                        company = re.sub(
                            r'\b(actively hiring|hiring now|urgent hiring)\b',
                            '',
                            company,
                            flags=re.IGNORECASE
                        )

                        # normalize spaces
                        company = re.sub(r'\s+', ' ', company).strip()

                        return company[:max_len]

                    def clean_skills(skills):
                        if not skills:
                            return "N/A"
                        skills = re.sub(r'\+\d+\s*more', '', skills.lower())
                        parts = skills.replace("\n", ",").split(",")
                        cleaned = sorted(set(s.strip() for s in parts if len(s.strip()) > 1))
                        return ", ".join(cleaned) if cleaned else "N/A"

                    def clean_stipend(text):
                        nums = re.findall(r'\d+', text.replace(',', ''))
                        if len(nums) >= 2:
                            return f"{nums[0]}-{nums[1]}"
                        elif len(nums) == 1:
                            return nums[0]
                        return "unpaid"

                    job_data = {
                        "title": clean_text(title, 200),
                        "company": clean_company_name(company, 100),
                        "link": link,
                        "source": "internshala",
                        "location": "remote",
                        "duration": clean_text(duration, 50),
                        "stipend": clean_stipend(stipend),
                        "apply_by": None,
                        "skills": clean_skills(skills)
                    }

                    jobs_to_process.append(job_data)
                    count += 1
                except:
                    continue

            await page.close()

            # --- Deep Scrape Dates ---
            print(f"   ⏳ Verifying Dates for {len(jobs_to_process)} jobs for '{keyword}'...")
            chunk_size = 3
            for i in range(0, len(jobs_to_process), chunk_size):
                chunk = jobs_to_process[i:i + chunk_size]
                tasks = [fetch_details(context, job['link']) for job in chunk]
                results = await asyncio.gather(*tasks)

                for job, (backup_skills, deep_date) in zip(chunk, results):
                    if job['skills'] == "N/A" and backup_skills:
                        job['skills'] = backup_skills
                    if deep_date:
                        job['apply_by'] = deep_date
                    elif not job['apply_by']:
                        job['apply_by'] = get_fallback_date()
                    save_job(db, job, keyword)

            total_saved += count
            print(f"   ✅ Saved {count} verified jobs for '{keyword}'")

        await browser.close()
        gc.collect()
        print(f"\n🎉 Total jobs saved across all keywords: {total_saved}")
        return total_saved
