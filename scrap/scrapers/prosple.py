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

        await page.goto(
            f"https://in.prosple.com/search-jobs?keywords={keyword}&locations=India",
            timeout=60000
        )
        await page.wait_for_selector(".SearchJobCard", timeout=20000)

        cards = await page.query_selector_all(".SearchJobCard")
        for card in cards[:limit]:
            try:
                title = await (await card.query_selector("h2")).inner_text()
                link = await (await card.query_selector("a")).get_attribute("href")
                jobs.append({
                    "title": title.strip(),
                    "company": "Prosple Employer",
                    "link": f"https://in.prosple.com{link}",
                    "source": "Prosple",
                    "keyword": keyword,
                    "location": "India",
                    "duration": "N/A",
                    "stipend": "Hidden",
                    "skills": "N/A"
                })
            except:
                continue

        await browser.close()
    return jobs
