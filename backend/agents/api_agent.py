import os
import requests
import uuid
from typing import List, Dict, Optional

def run_api_agent(queries: List[str], passed_api_key: Optional[str] = None) -> List[Dict]:
    """
    Executes a search query against SearchApi's Google Jobs endpoint.
    Retrieves structured job definitions across the major job boards.
    """
    print(f"API Agent: Searching top jobs via SearchApi for {queries}...")
    
    # Check for passed API key first, then SEARCHAPI_KEY, fallback to SERPAPI_KEY
    api_key = passed_api_key or os.getenv("SEARCHAPI_KEY") or os.getenv("SERPAPI_KEY")
    api_jobs = []
    
    if not api_key:
        print("API Agent: No SEARCHAPI_KEY found in .env. Returning simulated jobs.")
        return [
            {
                "id": "api_1",
                "title": "Senior UI Developer",
                "company": "LinkedIn Corp",
                "location": "San Francisco, CA (Remote)",
                "description": "Please set SEARCHAPI_KEY in .env to see real jobs.",
                "url": "https://linkedin.com",
                "source": "API_AGENT"
            }
        ]

    for query in queries:
        try:
            params = {
                "engine": "google_jobs",
                "q": query,
                "api_key": api_key,
                "hl": "en",
                "gl": "us"
            }
            
            # Using SearchApi.io endpoint (added 15s timeout for hardening)
            response = requests.get("https://www.searchapi.io/api/v1/search", params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get("jobs", [])
            for idx, job in enumerate(jobs):
                # SearchAPI doesn't always provide a stable job_id, so we can generate one or use position
                job_id = job.get("job_id", str(uuid.uuid4()))
                
                # Use apply_link if available, otherwise sharing_link
                url = job.get("apply_link", job.get("sharing_link", ""))
                
                api_jobs.append({
                    "id": job_id,
                    "title": job.get("title", "Unknown Role"),
                    "company": job.get("company_name", "Unknown Company"),
                    "location": job.get("location", "Unknown Location"),
                    "description": job.get("description", ""),
                    "url": url,
                    "source": "API_AGENT"
                })
        except Exception as e:
            print(f"API Agent Error processing query '{query}': {e}")
            
    return api_jobs
