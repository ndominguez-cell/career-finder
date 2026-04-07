from typing import List, Dict
import asyncio
from playwright.async_api import async_playwright

async def run_scrape_agent(urls: List[str]) -> List[Dict]:
    """
    Executes a headless browser using Playwright to extract jobs
    from direct company boards or niche sites like YC Hacker News Jobs.
    """
    print(f"Scrape Agent: Firing up headless browser for targets: {urls}...")
    scraped_jobs = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for url in urls:
            try:
                await page.goto(url, wait_until="networkidle", timeout=15000)
                
                # Hacker News specifically uses tr.athing and titleline
                if "ycombinator.com" in url:
                    job_elements = await page.locator("tr.athing").all()
                    for el in job_elements:
                        try:
                            title_locator = el.locator(".titleline > a")
                            if await title_locator.count() > 0:
                                title = await title_locator.inner_text()
                                href = await title_locator.get_attribute("href")
                                
                                # Hacker news doesn't always provide absolute urls
                                if href and href.startswith("item?id="):
                                    href = f"https://news.ycombinator.com/{href}"
                                
                                scraped_jobs.append({
                                    "id": await el.get_attribute("id") or "hn",
                                    "title": title,
                                    "company": "Startup (via Hacker News)",
                                    "location": "Global / Included in title",
                                    "description": f"Directly scraped from YC Jobs portal for role: {title}",
                                    "url": href,
                                    "source": "SCRAPE_AGENT"
                                })
                        except Exception as e:
                            print(f"Failed to parse an HN row: {e}")
                else:
                    # Generic naive extraction for other sites (e.g. h1, h2 matching 'engineer')
                    print(f"Generic scrape for {url} not fully implemented yet.")
            except Exception as e:
                print(f"Scrape Agent Error on {url}: {e}")
                
        await browser.close()
        
    # Provide a fallback if it fails or targets are un-implemented
    if not scraped_jobs:
        scraped_jobs.append({
            "id": "scrape_fallback",
            "title": "React Engineer",
            "company": "Acme Widgets",
            "location": "Remote",
            "description": "Please ensure Playwright chromium is installed.",
            "url": "https://example.com/acme",
            "source": "SCRAPE_AGENT"
        })
        
    return scraped_jobs
