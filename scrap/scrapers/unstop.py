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

        await page.goto(f"https://unstop.com/internships?searchTerm={keyword}", timeout=60000)
        await page.wait_for_selector("a[href*='/internships/']", timeout=20000)

        links = await page.query_selector_all("a[href*='/internships/']")
        for link in links[:limit]:
            try:
                title = await (await link.query_selector("strong")).inner_text()
                href = await link.get_attribute("href")
                jobs.append({
                    "title": title.strip(),
                    "company": "Unstop Partner",
                    "link": f"https://unstop.com{href}",
                    "source": "Unstop",
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
