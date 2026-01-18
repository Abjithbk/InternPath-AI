import asyncio
import requests
from common import push_jobs
from scrapers import internshala, unstop, prosple
import os

API_URL = os.environ["API_URL"]

async def main():
    keywords = requests.get(f"{API_URL}/active-keywords").json()

    for kw in keywords:
        jobs = []
        jobs += await internshala.scrape(kw)
        await asyncio.sleep(2)
        jobs += await unstop.scrape(kw)
        await asyncio.sleep(2)
        jobs += await prosple.scrape(kw)
        push_jobs(jobs)

asyncio.run(main())
