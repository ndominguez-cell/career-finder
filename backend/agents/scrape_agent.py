from typing import List, Dict
import asyncio
import uuid
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
                    # Generic naive extraction for other sites (e.g. looking for job-like items)
                    print(f"Generic scrape for {url}... extracting title and links.")
                    page_title = await page.title()
                    
                    # Try to find elements that look like job titles (e.g. h2 or h3 with certain keywords)
                    job_keywords = ["engineer", "developer", "technician", "scientist", "manager", "lead", "staff", "associate"]
                    
                    # Simple heuristic: find headers and anchor tags
                    selectors = ["h1", "h2", "h3", ".job-title", ".title", "[class*='job']"]
                    found_something = False
                    
                    for sel in selectors:
                        elements = await page.locator(sel).all()
                        for el in elements:
                            text = await el.inner_text()
                            if any(kw in text.lower() for kw in job_keywords) and len(text) < 100:
                                scraped_jobs.append({
                                    "id": f"gen_{uuid.uuid4().hex[:6]}",
                                    "title": text.strip(),
                                    "company": page_title.split("|")[0].strip() or "Various",
                                    "location": "Remote / Hybrid",
                                    "description": f"Found on {url}. Content-based match.",
                                    "url": url,
                                    "source": "SCRAPE_AGENT"
                                })
                                found_something = True
                                if len(scraped_jobs) > 20: break
                        if found_something: break
                    
                    if not found_something:
                        print(f"No obvious jobs found on {url}")
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
