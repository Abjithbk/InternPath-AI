import asyncio
import random
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from . import models

# --- SPEED CONFIGURATION ---
async def block_media(route):
    """Blocks images/fonts to make scraping 5x faster."""
    if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
        await route.abort()
    else:
        await route.continue_()

# ==========================================
# 1. INTERNSHALA (Mobile Mode)
# ==========================================
async def scrape_internshala(context, keyword, db):
    print(f"   👉 [Internshala] Searching (Mobile Mode)...")
    page = await context.new_page()
    
    # 1. Block Media for Speed
    await page.route("**/*", block_media)

    # 2. Go to Mobile URL
    fmt_keyword = keyword.replace(" ", "-")
    url = f"https://internshala.com/internships/keywords-{fmt_keyword}"
    
    try:
        await page.goto(url, timeout=45000)
        # Random mouse/touch move to look human
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        
        # Wait for the container (Mobile often loads differently)
        await page.wait_for_selector(".individual_internship", timeout=15000)
    except:
        print("      ⚠️ [Internshala] Timeout or Blocked.")
        await page.close()
        return 0

    # 3. Scrape
    cards = await page.query_selector_all(".individual_internship")
    count = 0
    for card in cards:
        try:
            # Check for ID to avoid ads
            if not await card.get_attribute("internshipid"): continue

            title_el = await card.query_selector("h3") or await card.query_selector(".profile")
            if not title_el: continue
            title = await title_el.inner_text()

            # Mobile view often hides company name, try to find it
            company_el = await card.query_selector(".company_name")
            company = await company_el.inner_text() if company_el else "Internshala Employer"
            
            # Extract Link
            link_el = await card.query_selector(".view_detail_button") or await card.query_selector("a")
            if not link_el: continue
            
            rel_link = await link_el.get_attribute("href")
            full_link = f"https://internshala.com{rel_link}"
            
            if save_job(db, title.strip(), company.strip(), full_link, "Internshala (Mobile)"):
                count += 1
        except: continue

    print(f"   ✅ [Internshala] Found {count} live jobs.")
    await page.close()
    return count

# ==========================================
# 2. UNSTOP (Mobile Mode)
# ==========================================
async def scrape_unstop(context, keyword, db):
    print(f"   👉 [Unstop] Searching (Mobile Mode)...")
    page = await context.new_page()
    await page.route("**/*", block_media)

    url = f"https://unstop.com/internships?searchTerm={keyword}"
    
    try:
        await page.goto(url, timeout=45000)
        # Scroll down to trigger lazy loading
        await page.evaluate("window.scrollTo(0, 500)")
        await page.wait_for_selector("a[href*='/internships/']", timeout=15000)
    except:
        print("      ⚠️ [Unstop] Timeout or Blocked.")
        await page.close()
        return 0

    links = await page.query_selector_all("a[href*='/internships/']")
    count = 0
    for link in links:
        try:
            href = await link.get_attribute("href")
            # Filter garbage
            if "search" in href or len(href) < 30: continue
            
            title_el = await link.query_selector("strong") or await link.query_selector("h2")
            if not title_el: continue

            title = await title_el.inner_text()
            full_link = href if href.startswith("http") else f"https://unstop.com{href}"
            
            if save_job(db, title.strip(), "Unstop Partner", full_link, "Unstop (Mobile)"):
                count += 1
        except: continue
        
    print(f"   ✅ [Unstop] Found {count} live jobs.")
    await page.close()
    return count

# ==========================================
# HELPER: INSTANT SAVE
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
            db.commit() # Save to Supabase IMMEDIATELY
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
    print(f"🚀 [Scraper] Starting Mobile Emulation Search: {keyword}")
    total = 0
    
    async with async_playwright() as p:
        # Use a "Pixel 5" emulation. This tricks sites into thinking we are a phone.
        # This is often LESS blocked than a desktop browser.
        pixel_5 = p.devices['Pixel 5']
        
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(
            **pixel_5, # Apply mobile settings (Viewport, UserAgent, Touch)
            locale="en-IN",
            timezone_id="Asia/Kolkata"
        )

        # Run ONE BY ONE to ensure CPU can handle the emulation
        total += await scrape_internshala(context, keyword, db)
        await asyncio.sleep(1) 
        total += await scrape_unstop(context, keyword, db)

        await browser.close()
        
    print(f"🏁 [Scraper] Finished. Total Live Jobs: {total}")
    return {"status": "success", "count": total}