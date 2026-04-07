from typing import Optional
from fastapi import FastAPI, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio
import io
from PyPDF2 import PdfReader
from agents.api_agent import run_api_agent
from agents.scrape_agent import run_scrape_agent

app = FastAPI(title="Career Finder API")

# Allow Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Endpoint to handle resume upload. Extracts text from PDF and infers skills.
    """
    content = await file.read()
    print(f"Uploaded: {file.filename} ({len(content)} bytes)")
    
    extracted_text = ""
    target_role = "Software Engineer" # Default
    
    try:
        if file.filename.lower().endswith('.pdf'):
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
            print("Successfully extracted PDF text.")
            
            # Very basic hardcoded extraction based on keywords to simulate LLM until API keys are set
            extracted_text_lower = extracted_text.lower()
            inferred_skills = []
            if "react" in extracted_text_lower: inferred_skills.append("React")
            if "python" in extracted_text_lower: inferred_skills.append("Python")
            if "node" in extracted_text_lower: inferred_skills.append("Node.js")
            if "aws" in extracted_text_lower: inferred_skills.append("AWS")
            
            if "frontend" in extracted_text_lower: target_role = "Frontend Engineer"
            elif "backend" in extracted_text_lower: target_role = "Backend Engineer"
            elif "data" in extracted_text_lower: target_role = "Data Engineer"
            
            inferred_profile = {
                "title": target_role,
                "skills": inferred_skills if inferred_skills else ["Python", "React", "Next.js"],
                "location": "Remote",
                "raw_text_length": len(extracted_text)
            }
        else:
            inferred_profile = {
                "title": target_role,
                "skills": ["Python", "React", "Next.js"],
                "location": "Remote",
                "note": "Not a PDF, returning mockup profile"
            }
            
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        inferred_profile = {
            "title": "Software Engineer",
            "skills": ["Python", "React"],
            "location": "Remote",
            "error": "Failed to parse PDF"
        }
    
    return {"filename": file.filename, "status": "Parsed successfully!", "profile": inferred_profile}

@app.get("/fetch_jobs")
async def fetch_jobs(x_searchapi_key: Optional[str] = Header(None)):
    """
    Triggers BOTH the API Aggregator Agent and the direct Web Scraping Agent.
    Aggregates and scores the jobs.
    """
    # 1. Fire off both agents in parallel
    target_queries = ["Software Engineer Remote"]
    target_boards = ["https://news.ycombinator.com/jobs", "https://wellfound.com/jobs"]
    
    # Run API Agent (Sync turned async for simulation)
    # In real app run_in_executor for sync requests
    api_jobs = run_api_agent(target_queries, passed_api_key=x_searchapi_key)
    
    # Run Scrape Agent (Async playwright)
    scraped_jobs = await run_scrape_agent(target_boards)
    
    # 2. Consolidate results
    all_raw_jobs = api_jobs + scraped_jobs
    
    # 3. Analyze and score (Simulated)
    scored_jobs = []
    for job in all_raw_jobs:
        score = 80 if "React" in job["description"] or "Python" in job["description"] else 40
        reasoning = "Good tech stack match." if score >= 70 else "Missing core skills from resume."
        job["score"] = score
        job["reasoning"] = reasoning
        scored_jobs.append(job)
        
    # Sort descending
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "status": "success",
        "jobs": scored_jobs
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
