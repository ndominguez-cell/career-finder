import os
import requests
import uuid
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

def discover_job_urls(role: str, location: str) -> List[str]:
    api_key = os.getenv("SEARCHAPI_KEY") or os.getenv("SERPAPI_KEY")
    if not api_key:
        return ["https://news.ycombinator.com/jobs"]
    
    print(f"Scrape Agent: Discovery for {role} in {location}...")
    try:
        # Search specifically for greenhouse/lever boards or direct listings
        params = {
            "engine": "google",
            "q": f'"{role}" jobs in "{location}" (site:greenhouse.io | site:lever.co | "career page")',
            "api_key": api_key,
            "num": 8
        }
        response = requests.get("https://www.searchapi.io/api/v1/search", params=params)
        response.raise_for_status()
        data = response.json()
        
        links = []
        for result in data.get("organic_results", []):
            link = result.get("link")
            if link and not any(x in link for x in ["linkedin.com", "indeed.com", "ziprecruiter.com"]):
                links.append(link)
        return links or ["https://news.ycombinator.com/jobs"]
    except Exception as e:
        print(f"Scrape Agent Discovery Error: {e}")
        return ["https://news.ycombinator.com/jobs"]

def scrape_greenhouse_api(company_token: str) -> List[Dict]:
    try:
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs"
        resp = requests.get(api_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "id": f"gh_{j.get('id')}",
                    "title": j.get("title"),
                    "company": company_token.title(),
                    "location": j.get("location", {}).get("name", "Unknown"),
                    "description": f"Greenhouse listing for {j.get('title')}",
                    "url": j.get("absolute_url"),
                    "source": "SCRAPE_AGENT"
                })
            return jobs
    except: pass
    return []

def scrape_lever_api(company_token: str) -> List[Dict]:
    try:
        api_url = f"https://api.lever.co/v0/postings/{company_token}"
        resp = requests.get(api_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            jobs = []
            for j in data:
                jobs.append({
                    "id": f"lv_{j.get('id')}",
                    "title": j.get("text"),
                    "company": company_token.title(),
                    "location": j.get("categories", {}).get("location", "Unknown"),
                    "description": j.get("descriptionPlain", f"Lever listing for {j.get('text')}"),
                    "url": j.get("hostedUrl"),
                    "source": "SCRAPE_AGENT"
                })
            return jobs
    except: pass
    return []

async def run_scrape_agent(role: str, location: str) -> List[Dict]:
    """
    Scrapes jobs using dynamic board APIs and requests.
    Supports pinpoint locations via discovery.
    """
    urls = discover_job_urls(role, location)
    print(f"Scrape Agent: Processing {len(urls)} target URLs...")
    scraped_jobs = []
    
    for url in urls:
        try:
            # 1. Greenhouse Detection
            gh_match = re.search(r"greenhouse\.io/([^/?]+)", url)
            if gh_match:
                company = gh_match.group(1)
                scraped_jobs.extend(scrape_greenhouse_api(company))
                continue

            # 2. Lever Detection
            lv_match = re.search(r"lever\.co/([^/?]+)", url)
            if lv_match:
                company = lv_match.group(1)
                scraped_jobs.extend(scrape_lever_api(company))
                continue

            # 3. Hacker News
            if "ycombinator.com" in url:
                resp = requests.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select("tr.athing")
                for item in items:
                    title_el = item.select_one(".titleline > a")
                    if title_el:
                        title = title_el.get_text()
                        href = title_el.get("href")
                        if href and href.startswith("item?id="):
                            href = f"https://news.ycombinator.com/{href}"
                        scraped_jobs.append({
                            "id": f"hn_{item.get('id')}",
                            "title": title,
                            "company": "Startup (YC)",
                            "location": "Global",
                            "description": f"Scraped from Hacker News: {title}",
                            "url": href,
                            "source": "SCRAPE_AGENT"
                        })
                continue

            # 4. Fallback Generic (simple soup)
            print(f"Scrape Agent: Generic fallback for {url}")
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            page_title = soup.title.string if soup.title else "Company"
            
            # Find all links that look like jobs
            for a in soup.find_all('a', href=True):
                text = a.get_text().strip()
                if any(kw in text.lower() for kw in ["engineer", "developer", "technician", "scientist", "manager", "lead", "analyst"]) and 5 < len(text) < 100:
                    scraped_jobs.append({
                        "id": f"soup_{uuid.uuid4().hex[:6]}",
                        "title": text,
                        "company": page_title.split("|")[0].strip(),
                        "location": location,
                        "description": f"Found on {url}",
                        "url": a['href'] if a['href'].startswith('http') else f"{url.rstrip('/')}/{a['href'].lstrip('/')}",
                        "source": "SCRAPE_AGENT"
                    })
                    if len(scraped_jobs) > 50: break

        except Exception as e:
            print(f"Scrape Agent error on {url}: {e}")

    # Re-score or Filter results by location/role locally
    filtered_jobs = []
    role_kws = role.lower().split()
    loc_kws = location.lower().replace(",", " ").split()
    
    for job in scraped_jobs:
        title_lower = job['title'].lower()
        desc_lower = job['description'].lower()
        loc_lower = job['location'].lower()
        
        # Match role keywords
        role_match = any(kw in title_lower for kw in role_kws)
        # Match location keywords (relaxed match)
        loc_match = any(kw in loc_lower for kw in loc_kws) or "remote" in loc_lower or "remote" in location.lower()
        
        if role_match and (loc_match or not loc_kws):
            filtered_jobs.append(job)

    print(f"Scrape Agent: Returning {len(filtered_jobs)} filtered jobs.")
    return filtered_jobs[:40]
