import os
import requests
import re
from typing import List, Dict, Optional
from backend.agents.scrape_agent import scrape_greenhouse_api, scrape_lever_api

# Known Aerospace/Space companies and their ATS tokens
SPACE_COMPANIES = {
    "lever": [
        "spacex", 
        "relativityspace", 
        "axiomspace", 
        "anduril", 
        "astralanis",
        "vastspace",
        "muonspace"
    ],
    "greenhouse": [
        "rocketlab",
        "planetlabs",
        "fireflyaerospace",
        "sierraspace",
        "capellaspace",
        "orbitfab"
    ]
}

async def run_aerospace_agent(role: str, location: str) -> List[Dict]:
    """
    Expert agent for Aerospace/Space jobs.
    Directly queries major space company career portals via known ATS tokens.
    """
    print(f"Aerospace Agent: Scanning specialized space company boards for '{role}'...")
    
    aerospace_jobs = []
    
    # 1. Fetch from Lever companies
    for company in SPACE_COMPANIES["lever"]:
        try:
            jobs = scrape_lever_api(company)
            aerospace_jobs.extend(jobs)
        except Exception as e:
            print(f"Aerospace Agent: Error fetching {company} (Lever): {e}")

    # 2. Fetch from Greenhouse companies
    for company in SPACE_COMPANIES["greenhouse"]:
        try:
            jobs = scrape_greenhouse_api(company)
            aerospace_jobs.extend(jobs)
        except Exception as e:
            print(f"Aerospace Agent: Error fetching {company} (Greenhouse): {e}")

    # 3. Filter by role and location
    filtered_jobs = []
    role_kws = role.lower().split()
    loc_kws = location.lower().replace(",", " ").split()
    
    # Add common aerospace keywords to role matching if searching for "Aerospace"
    if "aerospace" in role.lower() or "space" in role.lower():
        role_kws.extend(["gnc", "propulsion", "orbital", "satellite", "avionics", "structures"])

    for job in aerospace_jobs:
        title_lower = job['title'].lower()
        desc_lower = job['description'].lower()
        loc_lower = job['location'].lower()
        
        # Match role keywords
        role_match = any(kw in title_lower for kw in role_kws)
        
        # Match location keywords (relaxed match)
        loc_match = not loc_kws or any(kw in loc_lower for kw in loc_kws) or "remote" in loc_lower or "remote" in location.lower()
        
        if role_match and loc_match:
            # Tag the source
            job["source"] = f"AEROSPACE_AGENT ({job['company']})"
            filtered_jobs.append(job)

    print(f"Aerospace Agent: Found {len(filtered_jobs)} matching aerospace jobs.")
    return filtered_jobs
