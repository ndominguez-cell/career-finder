import os
import json
from scraper import scrape_jobs
from analyzer import analyze_and_score

def run_pipeline():
    print("=== Career Finder Pipeline Started ===")
    
    # 1. Load config (could be from env vars or a file)
    search_params = {
        "role": os.getenv("TARGET_ROLE", "Software Engineer"),
        "location": os.getenv("TARGET_LOCATION", "Remote")
    }
    
    candidate_profile = {
        "skills": ["Python", "Backend", "APIs"],
        "location": "Remote",
        "experience_years": 4
    }
    
    # 2. Scrape jobs
    jobs = scrape_jobs(search_params)
    
    # Optional: Save intermediate raw jobs
    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/raw_jobs.json", "w") as f:
        json.dump(jobs, f, indent=4)
        
    print(f"Scraped {len(jobs)} jobs.")
    
    # 3. Analyze and score jobs
    scored_jobs = analyze_and_score(jobs, candidate_profile)
    
    # 4. Save deliverables
    os.makedirs("deliverables", exist_ok=True)
    out_path = "deliverables/report_latest.json"
    with open(out_path, "w") as f:
        json.dump(scored_jobs, f, indent=4)
        
    print(f"=== Pipeline Completed. Report saved to {out_path} ===")

if __name__ == "__main__":
    from dotenv import load_dotenv
    # Load secrets if present
    load_dotenv()
    run_pipeline()
