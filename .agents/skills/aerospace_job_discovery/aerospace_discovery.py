import asyncio
import os
import sys

# Add the project root to sys.path so we can import backend agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.agents.aerospace_agent import run_aerospace_agent

async def main():
    role = sys.argv[1] if len(sys.argv) > 1 else "Aerospace Engineer"
    location = sys.argv[2] if len(sys.argv) > 2 else "Remote"
    
    print(f"--- Aerospace Job Discovery Skill ---\nSearching for: {role} in {location}\n")
    
    jobs = await run_aerospace_agent(role, location)
    
    if not jobs:
        print("No jobs found with the current filters.")
        return

    print(f"Found {len(jobs)} specialized aerospace jobs:")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} @ {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['url']}")
        print("-" * 30)

if __name__ == "__main__":
    if not os.getenv("SEARCHAPI_KEY") and not os.getenv("SERPAPI_KEY"):
        print("Warning: SEARCHAPI_KEY/SERPAPI_KEY not found. Search results may be limited.")
    
    asyncio.run(main())
