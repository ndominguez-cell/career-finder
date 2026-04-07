import json
import os
from typing import List, Dict

def analyze_and_score(jobs: List[Dict], candidate_profile: Dict) -> List[Dict]:
    """
    Dummy function for the LLM analyzer.
    In reality, you would use OpenAI, Anthropic, or Gemini APIs here
    to match the job description against candidate_profile.
    """
    print("Analyzing jobs...")
    scored_jobs = []
    
    for job in jobs:
        # Mocking an LLM scoring call
        score = 80 if "Python" in job["description"] else 40
        reasoning = "Good match based on Python requirement." if score >= 70 else "Missing key skills."
        
        job["score"] = score
        job["reasoning"] = reasoning
        scored_jobs.append(job)
        
    # Sort by score descending
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    return scored_jobs

if __name__ == "__main__":
    if not os.path.exists(".tmp/raw_jobs.json"):
        print("No raw jobs found. Please run scraper first.")
        exit(1)
        
    with open(".tmp/raw_jobs.json", "r") as f:
        jobs = json.load(f)
        
    # Dummy profile
    candidate_profile = {
        "skills": ["Python", "Backend", "APIs"],
        "location": "Remote"
    }
    
    scored_jobs = analyze_and_score(jobs, candidate_profile)
    
    # Output to deliverables
    os.makedirs("deliverables", exist_ok=True)
    out_path = "deliverables/report_latest.json"
    with open(out_path, "w") as f:
        json.dump(scored_jobs, f, indent=4)
        
    print(f"Scored {len(scored_jobs)} jobs. Output saved to {out_path}.")
