import random
from patchright.async_api import async_playwright
from common import USER_AGENTS, BROWSER_ARGS

async def scrape(keyword, limit=10):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        url = f"https://internshala.com/internships/keywords-{keyword.replace(' ', '-')}"
        await page.goto(url, timeout=45000)
        await page.wait_for_selector(".individual_internship", timeout=20000)

        cards = await page.query_selector_all(".individual_internship")
        for card in cards[:limit]:
            try:
                title = await (await card.query_selector("h3")).inner_text()
                company = await (await card.query_selector(".company_name")).inner_text()
                href = await card.get_attribute("data-href")
                if not href:
                    continue

                jobs.append({
                    "title": title.strip(),
                    "company": company.strip(),
                    "link": f"https://internshala.com{href}",
                    "source": "Internshala",
                    "keyword": keyword,
                    "location": "India",
                    "duration": "N/A",
                    "stipend": "See Link",
                    "skills": "N/A"
                })
            except:
                continue

        await browser.close()
    return jobs
