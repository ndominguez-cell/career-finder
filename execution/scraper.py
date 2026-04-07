import json
import os
import requests
from typing import List, Dict

def scrape_jobs(search_params: Dict) -> List[Dict]:
    """
    Dummy function for scraper.
    In reality, here is where you would place Selenium, BeautifulSoup,
    or the Indeed/LinkedIn API calls.
    """
    print(f"Scraping jobs for params: {search_params}")
    
    # Placeholder mocked data
    jobs = [
        {
            "id": "job_1",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "Looking for a Python backend engineer with API experience.",
            "url": "https://example.com/job1"
        },
        {
            "id": "job_2",
            "title": "Data Scientist",
            "company": "Data Inc",
            "location": "New York, NY",
            "description": "Skilled in machine learning and data pipelines.",
            "url": "https://example.com/job2"
        }
    ]
    return jobs

if __name__ == "__main__":
    jobs = scrape_jobs({"role": "Engineer", "location": "Remote"})
    
    # Save to tmp directory
    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/raw_jobs.json", "w") as f:
        json.dump(jobs, f, indent=4)
        
    print("Scraped 2 jobs into .tmp/raw_jobs.json")
