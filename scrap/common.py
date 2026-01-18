import os
import requests
import random

API_URL = os.environ["API_URL"]
API_KEY = os.environ["API_KEY"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15"
]

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage"
]

def push_jobs(jobs):
    if not jobs:
        return
    requests.post(
        f"{API_URL}/ingest",
        json=jobs,
        headers={"X-API-KEY": API_KEY},
        timeout=30
    )
